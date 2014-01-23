#pylint: disable-msg=C0302
from courseaffils.lib import in_course, in_course_or_404, AUTO_COURSE_SELECT
from courseaffils.models import CourseAccess
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.core import serializers
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseForbidden, \
    HttpResponseRedirect, Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext, loader
from djangohelpers.lib import allow_http
from mediathread.api import UserResource, TagResource
from mediathread.assetmgr.api import AssetResource, AssetSummaryResource
from mediathread.assetmgr.models import Asset, Source
from mediathread.djangosherd.models import SherdNote, DiscussionIndex
from mediathread.djangosherd.views import create_annotation, edit_annotation, \
    delete_annotation, update_annotation
from mediathread.main import course_details
from mediathread.main.course_details import all_selections_are_visible, \
    cached_course_is_faculty
from mediathread.main.decorators import ajax_required
from mediathread.main.models import UserSetting
from mediathread.taxonomy.api import VocabularyResource, TermResource, \
    TermRelationshipResource
from mediathread.taxonomy.models import Vocabulary, TermRelationship
from tagging.models import Tag
import datetime
import hashlib
import hmac
import re
import simplejson
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


@login_required
@allow_http("GET")
def asset_workspace(request, asset_id=None, annot_id=None):
    if not request.user.is_staff:
        in_course_or_404(request.user.username, request.course)

    if asset_id:
        try:
            asset = Asset.objects.get(pk=asset_id, course=request.course)
        except Asset.DoesNotExist:
            return asset_switch_course(request, asset_id)

    data = {'space_owner': request.user.username,
            'asset_id': asset_id,
            'annotation_id': annot_id}

    if not request.is_ajax():
        return render_to_response('assetmgr/asset_workspace.html',
                                  data,
                                  context_instance=RequestContext(request))
    elif asset_id:
        # @todo - refactor this context out of the mix
        # ideally, the client would simply request the json
        context = detail_asset_json(request, asset)
    else:
        context = {'type': 'asset'}

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
                       'show_collection': True, }]

    return HttpResponse(simplejson.dumps(data, indent=2),
                        mimetype='application/json')


def asset_workspace_courselookup(asset_id=None, annot_id=None):
    """lookup function corresponding to asset_workspace
    if an asset is being requested then we can guess the course
    """
    if asset_id:
        return Asset.objects.get(pk=asset_id).course

AUTO_COURSE_SELECT[asset_workspace] = asset_workspace_courselookup


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

            asset.metadata_blob = simplejson.dumps(metadata)
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
                                   request.REQUEST['noui']), })
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

    json_stream = simplejson.dumps({})
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
        return HttpResponse(simplejson.dumps(response),
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


@login_required
@allow_http("GET")
@ajax_required
def asset_detail(request, asset_id):
    if not request.user.is_staff:
        in_course_or_404(request.user.username, request.course)

    try:
        asset = Asset.objects.get(pk=asset_id, course=request.course)
        the_json = detail_asset_json(request, asset)
        return HttpResponse(simplejson.dumps(the_json, indent=2),
                            mimetype='application/json')
    except Asset.DoesNotExist:
        return asset_switch_course(request, asset_id)


@login_required
@allow_http("GET")
@ajax_required
def asset_references(request, asset_id):
    if not request.user.is_staff:
        in_course_or_404(request.user.username, request.course)

    try:
        the_json = {}
        asset = Asset.objects.get(pk=asset_id, course=request.course)

        filters = {
            'assets': [asset.id],
            'counts': True
        }
        the_json['tags'] = TagResource(request.course).filter(request, filters)

        the_json['vocabulary'] = []
        for vocab in Vocabulary.objects.get_for_object(request.course):
            filters['vocabulary'] = vocab.id
            concepts = TermRelationshipResource(request.course).filter(request,
                                                                       filters)
            if len(concepts):
                the_json['vocabulary'].append(
                    {'display_name': vocab.display_name,
                     'term_set': concepts})

        # DiscussionIndex is misleading. Objects returned are
        # projects & discussions title, object_pk, content_type, modified
        collaboration_items = DiscussionIndex.with_permission(
            request,
            DiscussionIndex.objects.filter(asset=asset).order_by('-modified'))

        the_json['references'] = [{
            'id': obj.collaboration.object_pk,
            'title': obj.collaboration.title,
            'type': obj.get_type_label(),
            'url': obj.get_absolute_url(),
            'modified': obj.modified.strftime("%m/%d/%y %I:%M %p")}
            for obj in collaboration_items]

        return HttpResponse(simplejson.dumps(the_json, indent=2),
                            mimetype='application/json')
    except Asset.DoesNotExist:
        return asset_switch_course(request, asset_id)


@allow_http("GET")
@ajax_required
def assets_by_user(request, record_owner_name):
    """
    An ajax-only request to retrieve a specified user's assets
    Example:
        /asset/json/user/sld2131/
    """
    course = request.course
    if (request.user.is_staff and
        request.user.username == record_owner_name and
            not in_course(request.user.username, request.course)):
        return assets_by_course(request)

    in_course_or_404(record_owner_name, course)
    record_owner = get_object_or_404(User, username=record_owner_name)

    assets = Asset.objects.annotated_by(course,
                                        record_owner,
                                        include_archives=True)

    return render_assets(request, record_owner, assets)


@allow_http("GET")
@ajax_required
def assets_by_course(request):
    """
    An ajax-only request to retrieve a course's projects,
    assignment responses and selections
    """
    if not request.user.is_staff:
        in_course_or_404(request.user.username, request.course)

    assets = Asset.objects \
        .filter(course=request.course) \
        .extra(select={'lower_title': 'lower(assetmgr_asset.title)'}) \
        .select_related().order_by('lower_title')

    return render_assets(request, None, assets)


def render_assets(request, record_owner, assets):
    course = request.course
    logged_in_user = request.user

    # Is the current user faculty OR staff
    is_faculty = cached_course_is_faculty(course, logged_in_user)

    # Can the record_owner edit the records
    viewing_own_records = (record_owner == logged_in_user)
    viewing_faculty_records = record_owner and course.is_faculty(record_owner)

    # Allow the logged in user to add assets to his composition
    citable = request.GET.get('citable', '') == 'true'

    # Does the course allow viewing other user selections?
    owner_selections_are_visible = (
        course_details.all_selections_are_visible(course) or
        viewing_own_records or viewing_faculty_records or is_faculty)

    # Spew out json for the assets
    if request.GET.get('annotations', '') == 'true':
        resource = AssetResource(owner_selections_are_visible,
                                 record_owner,
                                 {'editable': viewing_own_records,
                                  'citable': citable})
    else:
        resource = AssetSummaryResource({'editable': viewing_own_records,
                                         'citable': citable})

    asset_json = resource.render_list(request, assets)

    active_filters = {}
    for key, val in request.GET.items():
        if (key == 'tag' or
                key == 'modified' or
                key.startswith('vocabulary-')):
            active_filters[key] = val

    user_resource = UserResource()

    # #todo -- figure out a cleaner way to do this. Ugli-ness
    # Collate tag set & vocabulary set for the result set.
    # Get all visible notes for the returned asset set
    # These notes may include global annotations for all users,
    # whereas the rendered set will not
    active_asset_ids = [a['id'] for a in asset_json]
    active_notes = []
    if record_owner:
        if owner_selections_are_visible:
            active_notes = SherdNote.objects.filter(
                asset__course=course, asset__id__in=active_asset_ids,
                author__id=record_owner.id)
    else:
        if all_selections_are_visible(course) or is_faculty:
            # Display all tags for the asset set including globals
            active_notes = SherdNote.objects.filter(
                asset__course=course, asset__id__in=active_asset_ids)
        else:
            whitelist = [f.id for f in course.faculty]
            whitelist.append(request.user.id)
            active_notes = SherdNote.objects.filter(
                asset__course=course,
                asset__id__in=active_asset_ids,
                author__id__in=whitelist)

    tags = []
    if len(active_notes) > 0:
        tags = Tag.objects.usage_for_queryset(active_notes)
        tags.sort(lambda a, b: cmp(a.name.lower(), b.name.lower()))

    active_vocabulary = []
    note_ids = [n.id for n in active_notes]
    content_type = ContentType.objects.get_for_model(SherdNote)
    term_resource = TermResource()
    for vocab in Vocabulary.objects.get_for_object(request.course):
        vocabulary = {
            'id': vocab.id,
            'display_name': vocab.display_name,
            'term_set': []
        }
        related = TermRelationship.objects.filter(term__vocabulary=vocab,
                                                  content_type=content_type,
                                                  object_id__in=note_ids)

        terms = []
        for rel in related:
            if rel.term.display_name not in terms:
                the_term = term_resource.render_one(request, rel.term)
                vocabulary['term_set'].append(the_term)
                terms.append(rel.term.display_name)

        active_vocabulary.append(vocabulary)

    # Assemble the context
    data = {'assets': asset_json,
            'active_tags': TagResource().render_list(request, tags),
            'active_filters': active_filters,
            'active_vocabulary': active_vocabulary,
            'space_viewer': user_resource.render_one(request, logged_in_user),
            'editable': viewing_own_records,
            'citable': citable,
            'is_faculty': is_faculty}

    if record_owner:
        data['space_owner'] = user_resource.render_one(request, record_owner)

    json_stream = simplejson.dumps(data, indent=2)
    return HttpResponse(json_stream, mimetype='application/json')


def detail_asset_json(request, asset):
    the_json = AssetResource().render_one(request, asset)
    the_json['user_analysis'] = asset.user_analysis_count(request.user)

    help_setting = \
        UserSetting.get_setting(request.user, "help_item_detail_view", True)

    return {'type': 'asset',
            'assets': {asset.pk: the_json},
            'user_settings': {'help_item_detail_view': help_setting}}
