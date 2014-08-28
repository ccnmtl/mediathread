#pylint: disable-msg=C0302
from courseaffils.lib import in_course, in_course_or_404, AUTO_COURSE_SELECT
from courseaffils.models import CourseAccess
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core import serializers
from django.core.urlresolvers import reverse
from django.db.models.aggregates import Max
from django.http import HttpResponse, HttpResponseForbidden, \
    HttpResponseRedirect, Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext, loader
from django.views.generic.base import View
from djangohelpers.lib import allow_http
from mediathread.api import UserResource, TagResource
from mediathread.assetmgr.api import AssetResource
from mediathread.assetmgr.models import Asset, Source
from mediathread.discussions.api import DiscussionIndexResource
from mediathread.djangosherd.models import SherdNote, DiscussionIndex
from mediathread.djangosherd.views import create_annotation, edit_annotation, \
    delete_annotation, update_annotation
from mediathread.main.models import UserSetting
from mediathread.mixins import ajax_required, LoggedInMixin, \
    JSONResponseMixin, AjaxRequiredMixin, RestrictedMaterialsMixin
from mediathread.taxonomy.api import VocabularyResource
from mediathread.taxonomy.models import Vocabulary
import datetime
import hashlib
import hmac
import json
import re
import urllib
import urllib2


@login_required
@allow_http("POST")
def archive_add_or_remove(request):

    in_course_or_404(request.user.username, request.course)

    if 'remove' in request.POST.keys():
        title = request.POST.get('title')
        lst = Asset.objects.filter(title=title, course=request.course)
        for asset in lst:
            if asset.primary and asset.primary.is_archive():
                redirect = request.POST.get('redirect-url',
                                            reverse('class-manage-sources'))
                url = "%s?delsrc=%s" % (redirect, asset.title)
                asset.delete()
                return HttpResponseRedirect(url)
    else:
        return asset_create(request)


@login_required
def asset_switch_course(request, asset_id):
    try:
        asset = Asset.objects.get(pk=asset_id)
        in_course_or_404(request.user.username, asset.course)

        # the user is logged into the wrong class?
        rv = {}
        rv['switch_to'] = asset.course
        rv['switch_from'] = request.course
        rv['redirect'] = reverse('asset-view', args=[asset_id])
        return render_to_response('assetmgr/asset_not_found.html',
                                  rv,
                                  context_instance=RequestContext(request))
    except Asset.DoesNotExist:
        raise Http404("This item does not exist.")


def asset_workspace_courselookup(asset_id=None, annot_id=None):
    """lookup function corresponding to asset_workspace
    if an asset is being requested then we can guess the course
    """
    if asset_id:
        return Asset.objects.get(pk=asset_id).course


def _parse_metadata(req_dict):
    metadata = {}
    for key in req_dict:
        if key.startswith('metadata-'):
            metadata[key[len('metadata-'):]] = req_dict.getlist(key)
    return metadata


def _parse_user(request):
    user = request.user
    if ((user.is_staff or CourseAccess.allowed(request)) and
            'as' in request.REQUEST):
        as_user = request.REQUEST['as']
        user = get_object_or_404(User, username=as_user)

    if not request.course or not request.course.is_true_member(user):
        return HttpResponseForbidden("You must be a member of the course to \
            add assets.")
    return user


@login_required
@allow_http("GET", "POST")
def most_recent(request):
    user = request.user
    user_id = user.id
    asset = Asset.objects.filter(author_id=user_id).order_by('-modified')[0]
    asset_id = str(asset.id)
    return HttpResponseRedirect('/asset/' + asset_id + '/')


# @login_required #no login, so server2server interface is possible
@allow_http("POST")
def asset_create(request):
    """
    We'd like to support basically the Delicious URL API as much as possible
    /save?jump={yes|close}&url={url}&title={title}&{noui}&v={5}&share={yes}
    But also thumb={url}&stream={url}&...
    Other groups to pay attention to are MediaMatrix
    (seems subset of delicious: url=)
    """

    req_dict = getattr(request, request.method)
    user = _parse_user(request)
    metadata = _parse_metadata(req_dict)
    title = req_dict.get('title', '')
    asset = Asset.objects.get_by_args(req_dict, asset__course=request.course)

    if asset is False:
        raise AssertionError("no arguments were supplied to make an asset")

    if asset is None:
        try:
            asset = Asset(title=title[:1020],  # max title length
                          course=request.course,
                          author=user)
            asset.save()

            for source in sources_from_args(request, asset).values():
                if len(source.url) <= 4096:
                    source.save()

            if "tag" in metadata:
                for each_tag in metadata["tag"]:
                    asset.save_tag(user, each_tag)

            asset.metadata_blob = json.dumps(metadata)
            asset.save()
        except:
            # we'll make it here if someone doesn't submit
            # any primary_labels as arguments
            # @todo verify the above comment.
            raise AssertionError("no primary source provided")

    # create a global annotation
    asset.global_annotation(user, True)
    asset_url = reverse('asset-view', args=[asset.id])
    source = request.POST.get('asset-source', "")

    if source == 'bookmarklet':
        # bookmarklet create
        asset_url += "?level=item"

        template = loader.get_template('assetmgr/analyze.html')
        context = RequestContext(request, {
            'request': request,
            'user': user,
            'action': request.POST.get('button', None),
            'asset_url': asset_url
        })
        return HttpResponse(template.render(context))
    elif request.REQUEST.get('noui', '').startswith('postMessage'):
        # for bookmarklet mass-adding
        return render_to_response('assetmgr/interface_iframe.html',
                                  {'message': ('%s|%s' %
                                   (request.build_absolute_uri(asset_url)),
                                   request.REQUEST['noui']), },
                                  context_instance=RequestContext(request))
    elif request.is_ajax():
        # unsure when asset_create is called via ajax
        return HttpResponse(serializers.serialize('json', asset),
                            mimetype="application/json")
    elif "archive" == asset.primary.label:
        redirect_url = request.POST.get('redirect-url',
                                        reverse('class-manage-sources'))
        url = "%s?newsrc=%s" % (redirect_url, asset.title)
        return HttpResponseRedirect(url)
    else:
        # server2server create
        return HttpResponseRedirect(asset_url)


@login_required
@allow_http("GET", "POST")
@ajax_required
def asset_delete(request, asset_id):
    in_course_or_404(request.user.username, request.course)

    # Remove all annotations by this user
    # By removing the "global annotation" this effectively removes
    # The asset from the workspace
    asset = get_object_or_404(Asset, pk=asset_id, course=request.course)
    annotations = asset.sherdnote_set.filter(author=request.user)
    annotations.delete()

    json_stream = json.dumps({})
    return HttpResponse(json_stream, mimetype='application/json')


OPERATION_TAGS = ('jump', 'title', 'noui', 'v', 'share',
                  'as', 'set_course', 'secret')


# NON_VIEW
def good_asset_arg(key):
    # need support for some things like width,height,max_zoom
    return (not (key.startswith('annotation-')
                 or key.startswith('save-')
                 or key.startswith('metadata-')  # asset metadata
                 or key.endswith('-metadata')  # source metadata
                 )
            and key not in OPERATION_TAGS)


def sources_from_args(request, asset=None):
    '''
    utilized by add_view to help create a new asset
    returns a dict of sources represented in GET/POST args
    '''
    sources = {}
    args = request.REQUEST
    for key, val in args.items():
        if good_asset_arg(key) and val != '':
            source = Source(label=key, url=val)
            # UGLY non-functional programming for url_processing
            source.request = request
            if asset:
                source.asset = asset
            src_metadata = args.get(key + '-metadata', None)
            if src_metadata:
                # w{width}h{height};{mimetype} (with mimetype and w+h optional)
                the_match = re.match('(w(\d+)h(\d+))?(;(\w+/[\w+]+))?',
                                     src_metadata).groups()
                if the_match[1]:
                    source.width = int(the_match[1])
                    source.height = int(the_match[2])
                if the_match[4]:
                    source.media_type = the_match[4]
            sources[key] = source

    for lbl in Asset.primary_labels:
        if lbl in args:
            sources[lbl].primary = True
            break
    return sources


@login_required
@allow_http("POST")
def annotation_create(request, asset_id):
    """
    delegate to djangosherd view and redirect back to asset workspace

    but first, stuff a range into the request
    and get the annotation context from the url
    """

    # Verify asset exists
    get_object_or_404(Asset, pk=asset_id, course=request.course)

    form = request.POST.copy()
    form['annotation-context_pk'] = asset_id
    request.POST = form

    form = request.GET.copy()
    form['annotation-next'] = reverse('asset-view', args=[asset_id])
    request.GET = form

    return create_annotation(request)


@login_required
@allow_http("POST")
@ajax_required
def annotation_create_global(request, asset_id):
    try:
        asset = get_object_or_404(Asset, pk=asset_id, course=request.course)
        global_annotation = asset.global_annotation(request.user, True)
        update_annotation(request, global_annotation)

        response = {
            'asset': {'id': asset_id},
            'annotation': {
                'id': global_annotation.id,
                'creating': True
            }
        }
        return HttpResponse(json.dumps(response),
                            mimetype="application/json")

    except SherdNote.DoesNotExist:
        return HttpResponseForbidden("forbidden")


@login_required
@allow_http("POST")
def annotation_save(request, asset_id, annot_id):
    try:
        # Verify annotation exists
        ann = SherdNote.objects.get(pk=annot_id,
                                    asset=asset_id,
                                    asset__course=request.course)

        if (ann.is_global_annotation() and
            'asset-title' in request.POST and
                (request.user.is_staff or request.user == ann.asset.author)):
            ann.asset.title = request.POST.get('asset-title')
            ann.asset.save()

        form = request.GET.copy()
        form['next'] = '.'
        request.GET = form
        return edit_annotation(request, annot_id)  # djangosherd.views
    except SherdNote.DoesNotExist:
        return HttpResponseForbidden("forbidden")


@login_required
@allow_http("POST")
def annotation_delete(request, asset_id, annot_id):
    try:
        # Verify annotation exists
        SherdNote.objects.get(pk=annot_id,
                              asset=asset_id,
                              asset__course=request.course)

        redirect_to = reverse('asset-view', args=[asset_id])

        form = request.GET.copy()
        form['next'] = redirect_to
        request.GET = form
        return delete_annotation(request, annot_id)  # djangosherd.views
    except SherdNote.DoesNotExist:
        return HttpResponseForbidden("forbidden")


@login_required
@allow_http("GET", "POST")
def source_redirect(request):
    url = request.REQUEST.get('url', None)

    if not url:
        url = '/'
    else:
        source = None
        try:
            source = Source.objects.get(primary=True,
                                        label='archive',
                                        url=url,
                                        asset__course=request.course)
        except Source.DoesNotExist:
            return HttpResponseForbidden()
        special = getattr(settings, 'SERVER_ADMIN_SECRETKEYS', {})
        for server in special.keys():
            if url.startswith(server):
                url = source_specialauth(request, url, special[server])
                continue
        if url == source.url:
            return HttpResponseRedirect(source.url_processed(request))
    return HttpResponseRedirect(url)


def source_specialauth(request, url, key):
    nonce = '%smthc' % datetime.datetime.now().isoformat()
    redirect_back = "%s?msg=upload" % (request.build_absolute_uri('/'))

    username = request.user.username

    if ('as' in request.REQUEST and
            in_course(request.user.username, request.course) and
            (request.user.is_staff or
             request.user.has_perm('assetmgr.can_upload_for'))):
        username = request.REQUEST['as']

    return ("%s?set_course=%s&as=%s&redirect_url=%s"
            "&nonce=%s&hmac=%s&audio=%s&audio2=%s") % \
        (url,
         request.course.group.name,
         username,
         urllib.quote(redirect_back),
         nonce,
         hmac.new(key,
                  '%s:%s:%s' % (username, redirect_back, nonce),
                  hashlib.sha1).hexdigest(),
         request.POST.get('audio', ''),
         request.POST.get('audio2', ''))


def final_cut_pro_xml(request, asset_id):
    if not request.user.is_staff:
        return HttpResponseForbidden()

    '''support for http://developer.apple.com/mac/library/documentation/ \
    AppleApplications/Reference/FinalCutPro_XML/Topics/Topics.html'''
    try:
        from xmeml import VideoSequence
        # http://github.com/ccnmtl/xmeml
        asset = get_object_or_404(Asset, pk=asset_id)

        xmeml = asset.sources.get('xmeml', None)
        if xmeml is None:
            return HttpResponse("Not Found: This annotation's asset does not \
            have a Final Cut Pro source XML associated with it", status=404)

        the_file = urllib2.urlopen(xmeml.url)
        assert the_file.code == 200
        the_video = VideoSequence(xml_string=the_file.read())

        clips = []
        keys = request.POST.keys()
        keys.sort(key=lambda x: int(x))
        for key in keys:
            ann = asset.sherdnote_set.get(id=request.POST.get(key),
                                          range1__isnull=False)
            if ann:
                clip = the_video.clip(ann.range1, ann.range2, units='seconds')
                clips.append(clip)

        xmldom, dumb_uuid = the_video.clips2dom(clips)
        res = HttpResponse(xmldom.toxml(), mimetype='application/xml')
        res['Content-Disposition'] = \
            'attachment; filename="%s.xml"' % asset.title
        return res

    except ImportError:
        return HttpResponse('Not Implemented: No Final Cut Pro Xmeml support',
                            status=503)


class AssetReferenceView(LoggedInMixin, RestrictedMaterialsMixin,
                         AjaxRequiredMixin, JSONResponseMixin, View):

    def get(self, request, asset_id):
        try:
            ctx = {}
            asset = Asset.objects.filter(pk=asset_id, course=request.course)
            notes = SherdNote.objects.get_related_notes(
                asset, self.record_owner, self.visible_authors)

            # tags
            ctx['tags'] = TagResource().render_related(request, notes)

            # vocabulary
            ctx['vocabulary'] = VocabularyResource().render_related(request,
                                                                    notes)

            # DiscussionIndex is misleading. Objects returned are
            # projects & discussions title, object_pk, content_type, modified
            indicies = DiscussionIndex.objects.filter(
                asset=asset).order_by('-modified')
            ctx.update(DiscussionIndexResource().render_list(request,
                                                             indicies))

            return self.render_to_json_response(ctx)
        except Asset.DoesNotExist:
            return asset_switch_course(request, asset_id)


class AssetWorkspaceView(LoggedInMixin, RestrictedMaterialsMixin,
                         JSONResponseMixin, View):

    def get(self, request, asset_id=None, annot_id=None):

        if asset_id:
            try:
                asset = Asset.objects.get(pk=asset_id, course=request.course)
                asset.primary
            except Asset.DoesNotExist:
                return asset_switch_course(request, asset_id)
            except Source.DoesNotExist:
                ctx = RequestContext(request)
                return render_to_response('500.html', {}, context_instance=ctx)

        data = {'asset_id': asset_id, 'annotation_id': annot_id}

        if not request.is_ajax():
            return render_to_response('assetmgr/asset_workspace.html',
                                      data,
                                      context_instance=RequestContext(request))
        context = {'type': 'asset'}
        if asset_id:
            # @todo - refactor this context out of the mix
            # ideally, the client would simply request the json
            # the mixin is expecting a queryset, so this becomes awkward here
            self.record_owner = request.user
            assets = Asset.objects.filter(pk=asset_id)
            (assets, notes) = self.visible_assets_and_notes(request, assets)
            context['assets'] = {
                asset.pk: AssetResource().render_one(request, asset, notes)
            }

            help_setting = UserSetting.get_setting(request.user,
                                                   "help_item_detail_view",
                                                   True)
            context['user_settings'] = {'help_item_detail_view': help_setting}

        vocabulary = VocabularyResource().render_list(
            request, Vocabulary.objects.get_for_object(request.course))

        user_resource = UserResource()
        owners = user_resource.render_list(request, request.course.members)

        data['panels'] = [{'panel_state': 'open',
                           'panel_state_label': "Annotate Media",
                           'context': context,
                           'owners': owners,
                           'vocabulary': vocabulary,
                           'template': 'asset_workspace',
                           'current_asset': asset_id,
                           'current_annotation': annot_id,
                           'update_history': True,
                           'show_collection': True}]

        return self.render_to_json_response(data)


class AssetDetailView(LoggedInMixin, RestrictedMaterialsMixin,
                      AjaxRequiredMixin, JSONResponseMixin, View):

    def get(self, request, asset_id):
        self.record_owner = request.user
        the_assets = Asset.objects.filter(pk=asset_id, course=request.course)
        if the_assets.count() == 0:
            return asset_switch_course(request, asset_id)

        (assets, notes) = self.visible_assets_and_notes(request, the_assets)

        # if asset is not in my collection, it must be in my course
        if assets.count() == 0 and the_assets[0].course != request.course:
            return HttpResponseForbidden("forbidden")

        asset = the_assets[0]

        help_setting = UserSetting.get_setting(request.user,
                                               "help_item_detail_view",
                                               True)

        ctx = AssetResource().render_one(request, asset, notes)
        ctx = {
            'user_settings': {'help_item_detail_view': help_setting},
            'type': 'asset',
            'assets': {
                asset.pk: AssetResource().render_one(request, asset, notes)
            }
        }

        return self.render_to_json_response(ctx)


class AssetCollectionView(LoggedInMixin, RestrictedMaterialsMixin,
                          AjaxRequiredMixin, JSONResponseMixin, View):
    """
    An ajax-only request to retrieve assets for a course or a specified user
    Example:
        /api/asset/user/sld2131/
        /api/asset/a/
        /api/asset/
    """

    valid_filters = ['tag', 'modified']

    def get_context(self, request, assets, notes):
        # Allow the logged in user to add assets to his composition
        citable = request.GET.get('citable', '') == 'true'

        # Include annotation metadata. (makes response much larger)
        include_annotations = request.GET.get('annotations', '') == 'true'

        # Initialize the context
        ures = UserResource()
        ctx = {
            'space_viewer': ures.render_one(request, self.record_viewer),
            'is_faculty': self.is_viewer_faculty
        }

        if self.record_owner:
            ctx['space_owner'] = ures.render_one(request, self.record_owner)

        ctx['active_filters'] = {}
        for key, val in request.GET.items():
            if (key in self.valid_filters or key.startswith('vocabulary-')):
                ctx['active_filters'][key] = val

        ctx['editable'] = self.viewing_own_records
        ctx['citable'] = citable

        # render the assets
        ares = AssetResource(include_annotations=include_annotations,
                             extras={'editable': self.viewing_own_records,
                                     'citable': citable})
        ctx['assets'] = ares.render_list(request,
                                         self.record_viewer,
                                         assets, notes)

        return ctx

    def add_metadata(self, request, assets):
        # metadata for all notes associated with these assets
        # is displayed in the filtered list.
        # Not sure this is exactly right...will discuss with team
        notes = SherdNote.objects.get_related_notes(
            assets, self.record_owner or None, self.visible_authors)

        tags = TagResource().render_related(request, notes)
        vocab = VocabularyResource().render_related(request, notes)
        return {'active_tags': tags, 'active_vocabulary': vocab}

    def apply_pagination(self, assets, notes, offset, limit):
        # sort the object list via aggregation on the visible notes
        assets = notes.values('asset')
        assets = assets.annotate(last_modified=Max('modified'))
        assets = assets.order_by('-last_modified')

        # slice the list
        assets = assets[offset:offset + limit]
        ids = [a['asset'] for a in assets]
        return (assets, notes.filter(asset__id__in=ids))

    def get(self, request):
        if (self.record_owner):
            assets = Asset.objects.by_course_and_user(request.course,
                                                      self.record_owner)
        else:
            assets = Asset.objects.by_course(request.course)

        (assets, notes) = self.visible_assets_and_notes(request, assets)

        offset = int(request.GET.get("offset", 0))
        limit = int(request.GET.get("limit", 20))

        ctx = {}
        if offset == 0:
            # add relevant tags & metadata for all visible notes
            # needs to come before the pagination step
            ctx.update(self.add_metadata(request, assets))

        # slice down the list to speed rendering
        (assets, notes) = self.apply_pagination(assets, notes, offset, limit)

        # assemble the context
        ctx.update(self.get_context(request, assets, notes))

        return self.render_to_json_response(ctx)

AUTO_COURSE_SELECT[AssetWorkspaceView.as_view()] = asset_workspace_courselookup


class TagCollectionView(LoggedInMixin, RestrictedMaterialsMixin,
                        AjaxRequiredMixin, JSONResponseMixin, View):

    def get(self, request):
        # Retrieve tags for this course
        assets = Asset.objects.filter(course=request.course)

        notes = SherdNote.objects.get_related_notes(
            assets, self.record_owner or None, self.visible_authors)

        context = {}
        if len(notes) > 0:
            context = {'tags': TagResource().render_related(request, notes)}
        return self.render_to_json_response(context)
