from courseaffils.lib import in_course, in_course_or_404, AUTO_COURSE_SELECT
from courseaffils.models import CourseAccess
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core import serializers
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseForbidden, \
    HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from djangohelpers.lib import allow_http
from mediathread.api import UserResource, TagResource
from mediathread.assetmgr.api import AssetResource
from mediathread.assetmgr.models import Asset, Source
from mediathread.djangosherd.models import SherdNote, DiscussionIndex
from mediathread.djangosherd.views import create_annotation, edit_annotation, \
    delete_annotation, update_annotation
from mediathread.main import course_details
from mediathread.main.course_details import render_tags_by_course
from mediathread.main.decorators import ajax_required
from mediathread.main.models import UserSetting
from mediathread.taxonomy.api import VocabularyResource
from mediathread.taxonomy.models import Vocabulary
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
    course_tags = render_tags_by_course(request)

    user_resource = UserResource()
    owners = user_resource.render_list(request, request.course.members)

    data['panels'] = [{'panel_state': 'open',
                       'panel_state_label': "Annotate Media",
                       'context': context,
                       'owners': owners,
                       'vocabulary': vocabulary,
                       'course_tags': course_tags,
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
                for t in metadata["tag"]:
                    asset.save_tag(user, t)

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


@allow_http("GET")
@ajax_required
def assets_by_user(request, record_owner_name):
    """
    An ajax-only request to retrieve a specified user's assets
    Example:
        /asset/json/user/sld2131/
    """
    course = request.course
    if (request.user.username == record_owner_name and
        request.user.is_staff and
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
    is_faculty = course.is_faculty(logged_in_user)

    # Can the record_owner edit the records
    viewing_own_records = (record_owner == logged_in_user)
    viewing_faculty_records = record_owner and course.is_faculty(record_owner)

    # Allow the logged in user to add assets to his composition
    citable = request.GET.get('citable', '') == 'true'

    # include the asset annotations
    include_annotations = request.GET.get('annotations', '') == 'true'

    # Does the course allow viewing other user selections?
    owner_selections_are_visible = (
        course_details.all_selections_are_visible(course) or
        viewing_own_records or viewing_faculty_records or is_faculty)

    # Spew out json for the assets
    resource = AssetResource(include_annotations,
                             False,  # include archives
                             owner_selections_are_visible,
                             record_owner,
                             {'editable': viewing_own_records,
                              'citable': citable})
    asset_json = resource.render_list(request, assets)

    active_filters = {}
    for key, val in request.GET.items():
        if (key == 'tag' or
            key == 'modified' or
                key.startswith('vocabulary-')):
            active_filters[key] = val

    user_resource = UserResource()

    # Assemble the context
    data = {'assets': asset_json,
            'active_filters': active_filters,
            'space_viewer': user_resource.render_one(request, logged_in_user),
            'editable': viewing_own_records,
            'citable': citable,
            'is_faculty': is_faculty}

    if record_owner:
        data['space_owner'] = user_resource.render_one(request, record_owner)

    json_stream = simplejson.dumps(data, indent=2)
    return HttpResponse(json_stream, mimetype='application/json')


def detail_asset_json(request, asset):
    the_json = AssetResource(True).render_one(request, asset)
    the_json['user_analysis'] = asset.user_analysis_count(request.user)

    # References Page
    # Class tags for the References page
    all_selections_visible = course_details.all_selections_are_visible(
        request.course) or request.course.is_faculty(request.user)

    if not all_selections_visible:
        owners = [request.user]
        owners.extend(request.course.faculty)
        the_json['tags'] = TagResource().render_list(
            request, asset.filter_tags_by_users(owners, True))

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

    help_setting = \
        UserSetting.get_setting(request.user, "help_item_detail_view", True)

    rv = {'type': 'asset',
          'assets': {asset.pk: the_json},
          'user_settings': {'help_item_detail_view': help_setting}}

    return rv
