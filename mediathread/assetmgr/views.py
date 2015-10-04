# pylint: disable-msg=C0302
import datetime
import hashlib
import hmac
import json
import re
import urllib
import urllib2

from courseaffils.lib import in_course_or_404, in_course, AUTO_COURSE_SELECT
from courseaffils.models import Course, CourseAccess
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db.models.aggregates import Max
from django.db.models.query_utils import Q
from django.http import HttpResponse, HttpResponseForbidden, \
    HttpResponseRedirect, Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext, loader
from django.views.generic.base import View
from djangohelpers.lib import allow_http

from mediathread.api import UserResource, TagResource
from mediathread.assetmgr.api import AssetResource
from mediathread.assetmgr.models import Asset, Source, ExternalCollection, \
    SuggestedExternalCollection
from mediathread.discussions.api import DiscussionIndexResource
from mediathread.djangosherd.models import SherdNote, DiscussionIndex
from mediathread.djangosherd.views import create_annotation, edit_annotation, \
    delete_annotation, update_annotation
from mediathread.main.models import UserSetting
from mediathread.mixins import ajax_required, LoggedInMixin, \
    JSONResponseMixin, AjaxRequiredMixin, RestrictedMaterialsMixin, \
    LoggedInMixinSuperuser
from mediathread.taxonomy.api import VocabularyResource
from mediathread.taxonomy.models import Vocabulary


class ManageExternalCollectionView(LoggedInMixin, View):

    def post(self, request):
        suggested_id = request.POST.get('suggested_id', None)
        collection_id = request.POST.get('collection_id', None)
        if 'remove' in request.POST.keys():
            exc = get_object_or_404(ExternalCollection, id=collection_id)
            msg = '%s has been disabled for your class.' % exc.title
            exc.delete()
        elif suggested_id:
            suggested = get_object_or_404(SuggestedExternalCollection,
                                          id=suggested_id)
            exc = ExternalCollection()
            exc.title = suggested.title
            exc.url = suggested.url
            exc.thumb_url = suggested.thumb_url
            exc.description = suggested.description
            exc.course = request.course
            exc.save()
            msg = '%s has been enabled for your class.' % exc.title
        else:
            exc = ExternalCollection()
            exc.title = request.POST.get('title')
            exc.url = request.POST.get('url')
            exc.thumb_url = request.POST.get('thumb')
            exc.description = request.POST.get('description')
            exc.course = request.course
            exc.uploader = request.POST.get('uploader', False)
            exc.save()
            msg = '%s has been enabled for your class.' % exc.title

        messages.add_message(request, messages.INFO, msg)

        redirect_url = request.POST.get('redirect-url',
                                        reverse('class-manage-sources'))
        return HttpResponseRedirect(redirect_url)


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


class AssetCreateView(View):
    OPERATION_TAGS = ('jump', 'title', 'noui', 'v', 'share',
                      'as', 'set_course', 'secret')

    @classmethod
    def good_asset_arg(cls, key):
        # need support for some things like width,height,max_zoom
        return (not (key.startswith('annotation-') or
                     key.startswith('save-') or
                     key.startswith('metadata-') or  # asset metadata
                     key.endswith('-metadata')  # source metadata
                     ) and
                key not in cls.OPERATION_TAGS)

    @classmethod
    def add_metadata(cls, source, src_metadata):
        if src_metadata:
            # w{width}h{height};{mimetype}
            # (with mimetype and w+h optional)
            the_match = re.match('(w(\d+)h(\d+))?(;(\w+/[\w+]+))?',
                                 src_metadata).groups()
            if the_match[1]:
                source.width = int(the_match[1])
                source.height = int(the_match[2])
            if the_match[4]:
                source.media_type = the_match[4]

    @classmethod
    def sources_from_args(cls, request, asset=None):
        '''
        utilized by add_view to help create a new asset
        returns a dict of sources represented in GET/POST args
        '''
        sources = {}
        args = request.REQUEST
        for key, val in args.items():
            if cls.good_asset_arg(key) and val != '' and len(val) < 4096:
                source = Source(label=key, url=val)

                # UGLY non-functional programming for url_processing
                if asset:
                    source.asset = asset

                src_metadata = args.get(key + '-metadata', None)
                cls.add_metadata(source, src_metadata)
                sources[key] = source

        # iterate the primary labels in order of priority
        # pickup the first matching one & use that
        for lbl in Asset.primary_labels:
            if lbl in sources:
                sources[lbl].primary = True
                return sources

        # no primary source found, return no sources
        return {}

    def add_sources(self, request, asset):
        for source in self.sources_from_args(request, asset).values():
            source.save()

    def add_tags(self, asset, user, metadata):
        if "tag" in metadata:
            for each_tag in metadata["tag"]:
                asset.save_tag(user, each_tag)

    ''' No login required so server2server interface is possible'''

    def post(self, request):
        req_dict = getattr(request, request.method)
        user = _parse_user(request)
        metadata = _parse_metadata(req_dict)
        title = req_dict.get('title', '')
        success, asset = Asset.objects.get_by_args(
            req_dict, asset__course=request.course)

        if success is False:
            raise AssertionError("no arguments were supplied to make an asset")

        if asset is None:
            asset = Asset(title=title[:1020],  # max title length
                          course=request.course,
                          author=user)
            asset.save()

            self.add_sources(request, asset)

            self.add_tags(asset, user, metadata)

            asset.metadata_blob = json.dumps(metadata)
            asset.save()

            try:
                asset.primary  # make sure a primary source was specified
            except Source.DoesNotExist:
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
        else:
            # server2server create (wardenclyffe)
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
    return HttpResponse(json_stream, content_type='application/json')


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
                            content_type="application/json")

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


class RedirectToExternalCollectionView(LoggedInMixin, View):
    """
        simple way to redirect to a stored (thus obfuscated) url
    """

    def get(self, request, collection_id):
        exc = get_object_or_404(ExternalCollection, id=collection_id)
        return HttpResponseRedirect(exc.url)


class RedirectToUploaderView(LoggedInMixin, View):

    def post(self, request, *args, **kwargs):
        collection_id = kwargs['collection_id']
        exc = get_object_or_404(ExternalCollection, id=collection_id)

        special = getattr(settings, 'SERVER_ADMIN_SECRETKEYS', {})
        if exc.url not in special.keys():
            raise Http404("The uploader does not exist.")

        username = request.user.username
        as_user = request.POST.get('as', None)
        if (as_user and in_course(request.user.username, request.course) and
            (request.user.is_staff or
             request.user.has_perm('assetmgr.can_upload_for'))):
            username = as_user

        redirect_back = "%s?msg=upload" % (request.build_absolute_uri('/'))

        nonce = '%smthc' % datetime.datetime.now().isoformat()

        digest = hmac.new(special[exc.url],
                          '%s:%s:%s' % (username, redirect_back, nonce),
                          hashlib.sha1).hexdigest()

        url = ("%s?set_course=%s&as=%s&redirect_url=%s"
               "&nonce=%s&hmac=%s&audio=%s") % (exc.url,
                                                request.course.group.name,
                                                username,
                                                urllib.quote(redirect_back),
                                                nonce,
                                                digest,
                                                request.POST.get('audio', ''))

        return HttpResponseRedirect(url)


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
        res = HttpResponse(xmldom.toxml(), content_type='application/xml')
        res['Content-Disposition'] = \
            'attachment; filename="%s.xml"' % asset.title
        return res

    except ImportError:
        return HttpResponse('Not Implemented: No Final Cut Pro Xmeml support',
                            status=503)


class ScalarExportView(LoggedInMixinSuperuser, View):

    def __init__(self):
        self.export = {}
        self.tag_num = 0
        self.anno_num = 0
        self.root = ''

    def parse_annotations(self, data, n):
        user_node = {}
        username = data.get('annotations')[n]['author']['username']
        try:
            author_user = User.objects.get(username=username)
            author_email = author_user.email
            hash_or_username = hashlib.sha1(author_email).hexdigest()
        except Exception:
            hash_or_username = username

        user_node['http://xmlns.com/foaf/0.1/name'] = [{"value": data.get(
            'annotations')[n]['author']['public_name'], "type": "literal"}]
        user_node['http://www.w3.org/1999/02/22-rdf-syntax-ns#type'] = [
            {"value": "http://xmlns.com/foaf/0.1/Person", "type": "uri"}]
        user_node['http://xmlns.com/foaf/0.1/mbox_sha1sum'] = [
            {"value": hash_or_username, "type": "literal"}]
        self.export[self.root + '/user/' + hash_or_username] = user_node

        annotation_node = {}
        annotation_node['http://purl.org/dc/terms/title'] = [
            {"value": data.get('annotations')[n]['title'],
             "type": "literal"}]
        annotation_node['http://purl.org/dc/terms/description'] = [
            {"value": "This is an annotation", "type": "literal"}]
        annotation_node['http://rdfs.org/sioc/ns#content'] = [
            {"value": data.get('annotations')[n]['metadata']['body'],
             "type": "literal"}]
        annotation_node[
            'http://www.w3.org/ns/prov#wasAttributedTo'
        ] = [{"value": self.root + data.get(
            'annotations'
            )[n]['author']['resource_uri'].rstrip('/') +
                '/user/' + hash_or_username,
                "type": "uri"}]
        a_annotation_node = {}
        a_annotation_node['http://www.openannotation.org/ns/hasBody'] = [
            {"value": self.root +
             data.get('annotations')[n]['url'].rstrip('/'),
             "type": "uri"}]
        time = ''
        time += self.root
        time += data.get('local_url').rstrip('/')
        time += '#t=npt:'
        time += str(data.get('annotations')[n]['annotation']['start'])
        time += ','
        time += str(data.get('annotations')[n]['annotation']['end'])
        # try:
        a_annotation_node[
                'http://www.openannotation.org/ns/hasTarget'
            ] = [{"value": time, "type": "uri"}]
        # except Exception:
        #     pass
        a_annotation_node[
            'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'
        ] = [
            {"value": "http://www.openannotation.org/ns/Annotation",
             "type": "uri"}]
        anno_urn = 'urn:mediathread:anno' + str(self.anno_num + 1)
        self.export[anno_urn.rstrip('/')] = a_annotation_node
        self.anno_num += 1

        tag = []
        tag = (data.get('annotations')[n]['metadata']['tags'])
        for k in range(0, len(tag)):
            self.parse_tag(k, tag, n)

        vocab = []
        vocab = data.get('annotations')[n]['vocabulary']
        self.parse_vocab(vocab, n, data)

        try:
            self.export[self.root + data.get('annotations')[n]
                        ['url'].rstrip('/')] = annotation_node
        except Exception:
            pass

    def parse_vocab(self, vocab, n, data):
        print vocab
        for j in range(0, len(vocab)):
                num = 0
                for t in vocab[j]['terms']:
                    num += 1
                    urn_vocab_node = {}
                    urn_vocab_node[
                        'http://www.openannotation.org/ns/hasBody'] = [
                        {"value": self.root +
                            '/term/' + vocab[j]['display_name'] +
                            '-' + t['name'],
                         "type": "literal"}]
                    urn_vocab_node[
                        'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'
                    ] = [
                        {
                            "value":
                            "http://www.openannotation.org/ns/Annotation",
                            "type": "uri"}]

                    term_node = {}
                    term_node[
                        'http://www.w3.org/1999/02/22' +
                        '-rdf-syntax-ns#Description'
                    ] = [
                        {"value": vocab[j]['display_name'] +
                            '-' + t['name'], "type": "literal"}]
                    term_node[
                        'http://www.w3.org/2000/01/rdf-schema#label'
                    ] = [
                        {"value": vocab[j]['display_name'] +
                            '-' + t['name'], "type": "literal"}]
                    try:
                        term_node[
                            'http://www.w3.org/2004/02/skos/core#related'
                        ] = [
                            {"value": t['skos_uri'].rstrip('/'),
                             "type": "uri"}]
                    except Exception:
                        pass
                    term_node[
                        'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'
                    ] = [
                        {"type": "uri",
                         "value":
                            "http://www.openannotation.org/ns/SemanticTag"}
                        ]
                    self.export[self.root + '/term/' + vocab[j]
                                ['display_name'] + '-' +
                                t['name']] = term_node
                    try:
                        urn_vocab_node[
                            'http://www.openannotation.org/ns/hasTarget'
                        ] = [
                            {"value": self.root +
                                data.get(
                                    'annotations')[n]['url'].rstrip('/'),
                             "type": "uri"}
                             ]
                    except Exception:
                        pass

                    self.export["urn:mediathread:term" +
                                str(num)] = urn_vocab_node

    def parse_tag(self, k, tag, n):
        tag_node = {}
        tag_node["http://www.w3.org/2000/01/rdf-schema#label"] = [
            {"value": tag[k]['name'], "type": "literal"}]
        self.export[self.root + '/tag/' + tag[k]['name']] = tag_node
        a_tag_node = {}
        try:
            a_tag_node[
                'http://www.openannotation.org/ns/hasTarget'] = [
                {"value": self.root + self.data.get(
                            'annotations')[n]['url'].rstrip('/'),
                 "type": "uri"}]
        except Exception:
            pass
        try:
            if (len(tag[k]['resource_uri']) > 1):
                a_tag_node[
                    'http://www.openannotation.org/ns/hasBody'
                ] = [
                    {
                        "value": self.root + '/tag/' + tag[k][
                            'resource_uri'].rstrip('/'), "type": "uri"}
                    ]
            else:
                a_tag_node[
                    'http://www.openannotation.org/ns/hasBody'] = [
                    {"value": self.root +
                     '/tag/' + tag[k]['name'].rstrip('/'),
                     "type": "uri"}]
        except Exception:
            pass
        a_tag_node[
            'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'] = [
            {"value": "http://www.openannotation.org/ns/Annotation",
             "type": "uri"}]
        self.tag_num += 1
        a_tag_urn = 'urn:mediathread:tag' + str(self.tag_num)
        self.export[a_tag_urn] = a_tag_node

    def parse_response(self, data):
        video_node = {}
        # for the video node
        video_node[
            'http://purl.org/dc/terms/title'
            ] = [{"value": data.get('title'), "type": "literal"}]
        video_node['http://purl.org/dc/terms/description'] = [
            {"value": data.get('description'), "type": "literal"}]
        video_node['http://simile.mit.edu/2003/10/ontologies/artstor#url'] = [
            {"value": data.get('sources')[
                                            data.get('primary_type')
                                        ]['url'], "type": "uri"}]
        video_node['http://purl.org/dc/terms/source'] = [
            {"value": data.get('primary_type'), "type": "literal"}]
        video_node['http://purl.org/dc/terms/date'] = [
            {"value": data.get('modified'), "type": "literal"}]
        video_node['http://purl.org/dc/terms/contributor'] = [
            {"value": data.get('author')['username'], "type": "literal"}]
        self.export[self.root + data.get('local_url').rstrip('/')] = video_node
        # for annotation node
        for n in range(0, data.get('annotation_count')):
            self.parse_annotations(data, n)

    def get(self, request):
        self.root = 'http://' + request.get_host()
        assets = Asset.objects.filter(course=request.course)
        course = Course.objects.get(id=request.course.id)
        api_response = []
        n = 0
        for course_mem in course.user_set.values():
            n += 1
            ar = AssetResource(include_annotations=True)
            ar.Meta.excludes = ['added', 'modified', 'course', 'active']
            notes = SherdNote.objects.get_related_notes(
                                                        assets,
                                                        course_mem['id'],
                                                        [course_mem['id']],
                                                        True
                                                        )

            api_response += (ar.render_list(request, [course_mem['id']],
                                            [request.user.id], assets, notes))

        if len(api_response) == 0:
            return HttpResponse("There are no videos in your collection")
        for i in range(0, len(api_response)):
            self.parse_response(api_response[i])
        return HttpResponse(json.dumps(self.export))


class AssetReferenceView(LoggedInMixin, RestrictedMaterialsMixin,
                         AjaxRequiredMixin, JSONResponseMixin, View):

    def get(self, request, asset_id):
        try:
            ctx = {}
            asset = Asset.objects.filter(pk=asset_id, course=request.course)
            notes = SherdNote.objects.get_related_notes(
                asset, self.record_owner, self.visible_authors,
                self.all_items_are_visible)

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
        ctx = {'type': 'asset'}
        if asset_id:
            # @todo - refactor this context out of the mix
            # ideally, the client would simply request the json
            # the mixin is expecting a queryset, so this becomes awkward here
            assets = Asset.objects.filter(pk=asset_id)
            (assets, notes) = self.visible_assets_and_notes(request, assets)

            # only return original author's global annotations
            notes = notes.exclude(~Q(author=request.user), range1__isnull=True)

            ares = AssetResource()
            ctx.update(ares.render_one_context(request, asset, notes))

            help_setting = UserSetting.get_setting(request.user,
                                                   "help_item_detail_view",
                                                   True)
            ctx['user_settings'] = {'help_item_detail_view': help_setting}

        vocabulary = VocabularyResource().render_list(
            request, Vocabulary.objects.get_for_object(request.course))

        user_resource = UserResource()
        owners = user_resource.render_list(request, request.course.members)

        update_history = True
        show_collection = True
        template = 'asset_workspace'

        data['panels'] = [{
            'panel_state': 'open',
            'panel_state_label': "Annotate Media",
            'context': ctx,
            'owners': owners,
            'vocabulary': vocabulary,
            'template': template,
            'current_asset': asset_id,
            'current_annotation': annot_id,
            'update_history': update_history,
            'show_collection': show_collection}]

        return self.render_to_json_response(data)


class AssetDetailView(LoggedInMixin, RestrictedMaterialsMixin,
                      AjaxRequiredMixin, JSONResponseMixin, View):

    def get(self, request, asset_id):
        the_assets = Asset.objects.filter(pk=asset_id, course=request.course)
        if the_assets.count() == 0:
            return asset_switch_course(request, asset_id)

        (assets, notes) = self.visible_assets_and_notes(request, the_assets)

        # if asset is not in my collection, it must be in my course
        if assets.count() == 0 and the_assets[0].course != request.course:
            return HttpResponseForbidden("forbidden")

        # only return original author's global annotations
        notes = notes.exclude(~Q(author=request.user), range1__isnull=True)

        asset = the_assets[0]

        help_setting = UserSetting.get_setting(request.user,
                                               "help_item_detail_view",
                                               True)

        ctx = AssetResource().render_one_context(request, asset, notes)
        ctx['user_settings'] = {'help_item_detail_view': help_setting}
        ctx['type'] = 'asset'

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
    valid_filters = ['tag', 'modified', 'search_text']

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
                                         self.record_owner,
                                         self.record_viewer,
                                         assets, notes)

        return ctx

    def add_metadata(self, request, assets):
        # metadata for all notes associated with these assets
        # is displayed in the filtered list.
        notes = SherdNote.objects.get_related_notes(
            assets, self.record_owner or None, self.visible_authors,
            self.all_items_are_visible)

        tags = TagResource().render_for_course(request, notes)
        vocab = VocabularyResource().render_for_course(request, notes)
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
            assets, self.record_owner or None, self.visible_authors,
            self.all_items_are_visible)

        context = {}
        if len(notes) > 0:
            context = {'tags': TagResource().render_related(request, notes)}
        return self.render_to_json_response(context)
