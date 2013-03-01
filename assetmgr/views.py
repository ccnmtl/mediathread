from courseaffils.lib import in_course, get_public_name, in_course_or_404, \
    AUTO_COURSE_SELECT
from courseaffils.models import CourseAccess
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core import serializers
from django.core.urlresolvers import reverse
from django.db import models
from django.http import Http404, HttpResponse, HttpResponseForbidden, \
    HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from djangohelpers.lib import allow_http
from djangosherd.views import create_annotation, delete_annotation, \
    edit_annotation, update_annotation
from mediathread_main import course_details
from mediathread_main.models import UserSetting
import datetime
import hashlib
import hmac
import re
import simplejson
import urllib
import urllib2


Asset = models.get_model('assetmgr', 'asset')
Comment = models.get_model('comments', 'comment')
DiscussionIndex = models.get_model('djangosherd', 'discussionindex')
Source = models.get_model('assetmgr', 'source')
SherdNote = models.get_model('djangosherd', 'sherdnote')
User = models.get_model('auth', 'user')


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
@allow_http("GET")
def asset_workspace(request, asset_id=None, annot_id=None):
    if not request.user.is_staff:
        in_course_or_404(request.user.username, request.course)

    try:
        if asset_id:
            asset = Asset.objects.get(pk=asset_id, course=request.course)
    except Asset.DoesNotExist:
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

    data = {'space_owner': request.user.username,
            'asset_id': asset_id,
            'annotation_id': annot_id}

    if not request.is_ajax():
        return render_to_response('assetmgr/asset_workspace.html',
                                  data,
                                  context_instance=RequestContext(request))
    else:
        if asset_id:
            asset_workspace_context = detail_asset_json(
                request, asset_id, {'include_annotations': True})
        else:
            asset_workspace_context = {'type': 'asset'}

        data['panels'] = [{'panel_state': 'open',
                           'panel_state_label': "Annotate Media",
                           'context': asset_workspace_context,
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


@login_required
@allow_http("GET")
def asset_json(request, asset_id):
    if not request.is_ajax():
        raise Http404()

    if not request.user.is_staff:
        in_course_or_404(request.user.username, request.course)

    try:
        asset = Asset.objects.get(pk=asset_id, course=request.course)
    except Asset.DoesNotExist:
        asset = Asset.objects.get(pk=asset_id)
        in_course_or_404(request.user.username, asset.course)

        # the user is logged into the wrong class?
        rv = {}
        rv['switch_to'] = asset.course
        rv['switch_from'] = request.course
        rv['redirect'] = reverse('asset-view', args=[asset_id])
        return render_to_response('assetmgr/asset_not_found.html',
                                  rv, context_instance=RequestContext(request))

    the_json = detail_asset_json(request, asset_id, {})
    return HttpResponse(simplejson.dumps(the_json, indent=2),
                        mimetype='application/json')


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

    asset = None
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
                for t in metadata["tag"]:
                    asset.save_tag(user, t)

            if len(metadata):
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
        asset_url += "?level=item"

    # for bookmarklet mass-adding
    if request.REQUEST.get('noui', '').startswith('postMessage'):
        return render_to_response('assetmgr/interface_iframe.html',
                                  {'message': ('%s|%s' %
                                   (request.build_absolute_uri(asset_url)),
                                   request.REQUEST['noui']), })
    elif request.is_ajax():
        return HttpResponse(serializers.serialize('json', asset),
                            mimetype="application/json")
    elif "archive" == asset.primary.label:
        redirect_url = request.POST.get('redirect-url',
                                        reverse('class-manage-sources'))
        url = "%s?newsrc=%s" % (redirect_url, asset.title)
        return HttpResponseRedirect(url)
    else:
        return HttpResponseRedirect(asset_url)


@login_required
@allow_http("GET", "POST")
def asset_delete(request, asset_id):
    if not request.is_ajax():
        raise Http404()

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
                m = re.match('(w(\d+)h(\d+))?(;(\w+/[\w+]+))?',
                             src_metadata).groups()
                if m[1]:
                    source.width = int(m[1])
                    source.height = int(m[2])
                if m[4]:
                    source.media_type = m[4]
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
    get_object_or_404(Asset,
                      pk=asset_id,
                      course=request.course)

    form = request.POST.copy()
    form['annotation-context_pk'] = asset_id
    request.POST = form

    form = request.GET.copy()
    form['annotation-next'] = reverse('asset-view', args=[asset_id])
    request.GET = form

    return create_annotation(request)


@login_required
@allow_http("POST")
def annotation_create_global(request, asset_id):
    if not request.is_ajax():
        return HttpResponseForbidden("forbidden")

    try:
        asset = get_object_or_404(Asset,
                                  pk=asset_id,
                                  course=request.course)

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
        SherdNote.objects.get(pk=annot_id,
                              asset=asset_id,
                              asset__course=request.course)

        form = request.GET.copy()
        form['next'] = '.'
        request.GET = form
        return edit_annotation(request, annot_id)  # djangosherd.views
    except SherdNote.DoesNotExist:
        return HttpResponseForbidden("forbidden")


@login_required
@allow_http("GET", "DELETE")
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
    user = request.user
    if not user.is_staff:
        return HttpResponseForbidden()

    "support for http://developer.apple.com/mac/library/documentation/ \
    AppleApplications/Reference/FinalCutPro_XML/Topics/Topics.html"
    try:
        from xmeml import VideoSequence
        # http://github.com/ccnmtl/xmeml
        asset = get_object_or_404(Asset, pk=asset_id)

        xmeml = asset.sources.get('xmeml', None)
        if xmeml is None:
            return HttpResponse("Not Found: This annotation's asset does not \
            have a Final Cut Pro source XML associated with it", status=404)

        f = urllib2.urlopen(xmeml.url)
        assert f.code == 200
        v = VideoSequence(xml_string=f.read())

        clips = []

        keys = request.POST.keys()
        keys.sort(key=lambda x: int(x))
        for key in keys:
            sherd_id = request.POST.get(key)
            ann = asset.sherdnote_set.get(id=sherd_id, range1__isnull=False)
            if ann:
                clip = v.clip(ann.range1, ann.range2, units='seconds')
                clips.append(clip)

        xmldom, dumb_uuid = v.clips2dom(clips)
        res = HttpResponse(xmldom.toxml(), mimetype='application/xml')
        res['Content-Disposition'] = \
            'attachment; filename="%s.xml"' % asset.title
        return res

    except ImportError:
        return HttpResponse('Not Implemented: No Final Cut Pro Xmeml support',
                            status=503)


###############
# # JSON renderings of asset w/its annotations
# # @todo: add tests for this & homepage json function
# # @todo: refactor the json renderings together
# # Take into account: asset.sherd_json in the model
# # AND any references in project_json & discussion_json renderings
# # Possibly use something like TastyPie to
# provide a nice REST interface for this.
def detail_asset_json(request, asset_id, options):
    asset = get_object_or_404(Asset, pk=asset_id)

    selections_visible = \
        (course_details.all_selections_are_visible(request.course) or
         request.course.is_faculty(request.user))

    asset_json = asset.sherd_json(request)
    asset_key = 'x_%s' % asset.pk

    asset_json['user_analysis'] = 0

    ga = asset.global_annotation(request.user, False)
    if ga:
        asset_json['global_annotation_id'] = ga.id
        asset_json['notes'] = ga.body
        asset_json['user_tags'] = tag_json(ga.tags_split())

        if (asset_json['notes'] and len(asset_json['notes']) > 0) or \
                (asset_json['user_tags'] and len(asset_json['user_tags']) > 0):
            asset_json['user_analysis'] += 1

    if not selections_visible:
        owners = [request.user]
        owners.extend(request.course.faculty)
        asset_json['tags'] = tag_json(asset.filter_tags_by_users(owners, True))

    # DiscussionIndex is misleading. Objects returned are
    # projects & discussions title, object_pk, content_type, modified
    collaboration_items = \
        DiscussionIndex.with_permission(request,
                                        DiscussionIndex.objects.filter(
                                        asset=asset).order_by('-modified'))

    asset_json['references'] = [{
        'id': obj.collaboration.object_pk,
        'title': obj.collaboration.title,
        'type': obj.get_type_label(),
        'url': obj.get_absolute_url(),
        'modified': obj.modified.strftime("%m/%d/%y %I:%M %p")}
        for obj in collaboration_items]

    annotations = [{
        'asset_key': asset_key,
        'range1': None,
        'range2': None,
        'annotation': None,
        'id': 'asset-%s' % asset.pk,
        'asset_id': asset.pk, }]

    if ('annotations' in request.GET or
        (options and
         ('include_annotations' in options) and
         options['include_annotations'])):

        # @todo: refactor this serialization into a common place.
        def author_name(request, annotation, key):
            if not annotation.author_id:
                return None
            return 'author_name', get_public_name(annotation.author, request)

        def primary_type(request, annotation, key):
            return "primary_type", asset.primary.label

        for ann in asset.sherdnote_set.filter(range1__isnull=False):
            visible = (selections_visible or
                       request.user == ann.author or
                       request.course.is_faculty(ann.author))

            if visible:
                if request.user == ann.author:
                    asset_json['user_analysis'] += 1
                ann_json = ann.sherd_json(request, 'x', ('title',
                                                         'author',
                                                         'tags',
                                                         author_name,
                                                         'body',
                                                         'modified',
                                                         'timecode',
                                                         primary_type))
                annotations.append(ann_json)

    help_setting = \
        UserSetting.get_setting(request.user, "help_item_detail_view", True)

    rv = {'type': 'asset',
          # we make assets plural here to be
          # compatible with the project JSON structure
          'assets': {asset_key: asset_json},
          'annotations': annotations,
          'user_settings': {'help_item_detail_view': help_setting}}

    return rv


def homepage_asset_json(request, asset, logged_in_user, record_owner, options):
    the_json = asset.sherd_json(request)

    gannotation, created = \
        SherdNote.objects.global_annotation(asset,
                                            record_owner or logged_in_user,
                                            auto_create=False)

    if gannotation and \
        ('owner_selections_are_visible' in options and
         options['owner_selections_are_visible']):
        the_json['global_annotation'] = \
            gannotation.sherd_json(request, 'x', ('tags', 'body'))

    all_annotations = asset.sherdnote_set.filter(range1__isnull=False)
    the_json['editable'] = options['can_edit']
    the_json['citable'] = options['citable']
    the_json['my_annotation_count'] = \
        len(all_annotations.filter(author=request.user))

    if options['owner_selections_are_visible']:
        # @todo: refactor this serialization into a common place.
        def author_name(request, annotation, key):
            if not annotation.author_id:
                return None
            return 'author_name', get_public_name(annotation.author, request)

        def primary_type(request, annotation, key):
            return "primary_type", asset.primary.label

        annotations = []
        for ann in all_annotations.filter(author=record_owner):
            ann_json = ann.sherd_json(request, 'x', ('title',
                                                     'author',
                                                     'tags',
                                                     author_name,
                                                     'body',
                                                     'modified',
                                                     'timecode',
                                                     primary_type))

            ann_json['citable'] = options['citable']
            annotations.append(ann_json)
        the_json['annotations'] = annotations
    else:
        owners = [request.user]
        owners.extend(request.course.faculty)
        the_json['tags'] = tag_json(asset.filter_tags_by_users(owners))

    if options['all_selections_are_visible']:
        # count is for all annotations
        the_json['annotation_count'] = len(all_annotations)
    else:
        owners = [request.user]
        owners.extend(request.course.faculty)
        the_json['annotation_count'] = \
            len(all_annotations.filter(author__in=owners))

    return the_json


def tag_json(tags):
    tag_last = len(tags) - 1
    rv = []
    for idx, tag in enumerate(tags):
        t = {}
        t['name'] = tag.name
        t['last'] = idx == tag_last

        if hasattr(tag, 'count'):
            t['count'] = tag.count
        rv.append(t)
    return rv
