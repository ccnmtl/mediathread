from django.contrib.auth.decorators import login_required
from django.core import serializers
from django.core.urlresolvers import reverse
from django.db import transaction
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.http import Http404
from django.shortcuts import render_to_response
from django.template import RequestContext

from django.contrib.contenttypes.models import ContentType
from threadedcomments import ThreadedComment
from structuredcollaboration.models import Collaboration
from mediathread_main.clumper import Clumper
from mediathread_main import course_details
from mediathread_main.models import UserSetting

from django.conf import settings

from django.shortcuts import get_object_or_404
from django.db import models

from random import choice
from string import letters

import operator
import re
import simplejson
import urllib

Asset = models.get_model('assetmgr','asset')
Source = models.get_model('assetmgr','source')
SherdNote = models.get_model('djangosherd','sherdnote')
DiscussionIndex = models.get_model('djangosherd','discussionindex')
User = models.get_model('auth','user')
from courseaffils.models import CourseAccess
from djangosherd.views import AnnotationForm, GlobalAnnotationForm

Comment = models.get_model('comments','comment')

from djangohelpers.lib import rendered_with
from djangohelpers.lib import allow_http

from assetmgr.lib import filter_by,get_active_filters

from tagging.models import Tag
from tagging.utils import calculate_cloud
from courseaffils.lib import in_course_or_404, AUTO_COURSE_SELECT, get_public_name

#@login_required #no login, so server2server interface is possible
@allow_http("GET", "POST")
def add_view(request):
    if request.method == "POST":
        return add_asset(request)

    asset = Asset.objects.get_by_args(request.GET,
                                      asset__course=request.course)

    if asset:
        return HttpResponseRedirect(reverse('asset-view', args=[asset.id]))
    elif asset is None and request.user.is_authenticated():
        return mock_analysis_space(request)

    raise Http404()

OPERATION_TAGS = ('jump','title','noui','v','share','as','set_course','secret')
#NON_VIEW
def good_asset_arg(key):
    #need support for some things like width,height,max_zoom
    return (not (key.startswith('annotation-')
                 or key.startswith('save-')
                 or key.startswith('metadata-') #asset metadata
                 or key.endswith('-metadata')  #source metadata
                 )
            and key not in OPERATION_TAGS)

#NON_VIEW
def sources_from_args(request,asset=None):
    "returns a dict of sources represented in GET/POST args"
    sources = {}
    args = request.REQUEST
    for key,val in args.items():
        if good_asset_arg(key) and val != '':
            source = Source(label=key,url=val)
            #UGLY non-functional programming for url_processing
            source.request = request 
            if asset:
                source.asset = asset
            src_metadata = args.get(key+'-metadata',None)
            if src_metadata:
                #w{width}h{height};{mimetype} (with mimetype and w+h optional)
                m = re.match('(w(\d+)h(\d+))?(;(\w+/[\w+]+))?',src_metadata).groups()
                if m[1]:
                    source.width = int(m[1])
                    source.height = int(m[2])
                if m[4]:
                    source.media_type = m[4]
            sources[key] = source
    for lbl in Asset.primary_labels:
        if args.has_key(lbl):
            sources[lbl].primary = True
            break
    return sources

@rendered_with('assetmgr/asset.html')
def mock_analysis_space(request):

    user_tags = calculate_cloud(
        Tag.objects.usage_for_queryset(
            request.user.sherdnote_set.filter(asset__course=request.course), 
            counts=True)
        )

    sources = sources_from_args(request)

    title = getattr(request,request.method).get('title','')

    mock_asset = dict(title=title,
                      source_set={'all': sources.values()},
                      html_source={'url':request.GET.get('url',None) },
                      )
    return {
        'mock': True,
        'asset': mock_asset,
        'user_tags': user_tags,
        'annotation_form': AnnotationForm(prefix="annotation"),
        'global_annotation_form': GlobalAnnotationForm(prefix="annotation"),
        }


# Why is this a manual commit?
@transaction.commit_manually
def add_asset(request):
    """
    We'd like to support basically the Delicious URL API as much as possible
    /save?jump={yes|close}&url={url}&title={title}&{noui}&v={5}&share={yes}
    But also thumb={url}&stream={url}&...
    Other groups to pay attention to are MediaMatrix (seems subset of delicious: url=)
    """
    
    # XXX TODO: the error case here should be 401/403, not 404
    user = request.user
    if (user.is_staff or CourseAccess.allowed(request)) and request.REQUEST.has_key('as'):
        as_user = request.REQUEST['as']
        if as_user == 'faculty':
            as_user = request.course.faculty[0].username
        user = get_object_or_404(User,username=as_user)

    if not request.course or not request.course.is_true_member(user):
        extra = ''
        if user.is_staff:
            extra = 'Since you are staff, you can add yourself through <a href="%s">Manage Course</a> interface.' % reverse('admin:courseaffils_course_change', args=[request.course.id])
        return HttpResponseForbidden("""You must be a member of the course to add assets.  
                  This is to prevent unintentional participation.%s""" % extra)

    asset = None

    req_dict = getattr(request,request.method)

    metadata = {}
    for key in req_dict:
        if key.startswith('metadata-'):
            metadata[key[len('metadata-'):]] = req_dict.getlist(key)

    title = req_dict.get('title','')
    asset = Asset.objects.get_by_args(req_dict, asset__course=request.course)

    if asset is False:
        raise AssertionError("no arguments were supplied to make an asset")
    
    

    if asset is None:
        try:
            asset = Asset(title=title[:1020], #max title length
                      course=request.course,
                      author=user)
            asset.save()
            for source in sources_from_args(request, asset).values(): 
                if len(source.url) <= 4096:
                    source.save()
                    
            if "tag" in metadata:
                for t in metadata["tag"]:
                    asset.save_tag(user, t)

            transaction.commit()
            if len(metadata):
                asset.metadata_blob = simplejson.dumps(metadata)
                asset.save()
                transaction.commit()
        except:
            transaction.rollback()
            raise
    else:
        transaction.commit()

    

    # if we got here from an attempt to annotate the mock asset
    # we'll save that annotation now that the asset exists
    if asset:
        if request.POST.has_key('save-global-annotation'):
            # if the user is saving a global annotation
            # we need to create it first and then edit it
            global_annotation = asset.global_annotation(user)
            annotationview(request, asset.pk, global_annotation.pk)
            transaction.commit()
        elif request.POST.has_key('save-clip-annotation'):
            create_annotations_container(request, asset.pk)
            transaction.commit()

        asset_url = reverse('asset-view', args=[asset.id])
        
        source = request.POST.get('asset-source', "")
        if source == 'bookmarklet':
            asset_url += "?level=item"
    
        #for bookmarklet mass-adding
        if request.REQUEST.get('noui','').startswith('postMessage'):
            return render_to_response('assetmgr/interface_iframe.html',
                                      {'message': '%s|%s' % (request.build_absolute_uri(asset_url),
                                                             request.REQUEST['noui']),
                                      })
        elif request.is_ajax():
            return HttpResponse(serializers.serialize('json',asset),
                                mimetype="application/json")
            
        elif "archive" == asset.primary.label:
            redirect_url = request.POST.get('redirect-url', reverse('class-add-source'))
            url = "%s?newsrc=%s" % (redirect_url, asset.title)
            transaction.commit()
            return HttpResponseRedirect(url)
        else:
            transaction.commit()
            return HttpResponseRedirect(asset_url)
    else:
        #we'll make it here if someone doesn't submit
        #any primary_labels as arguments
        raise AssertionError("something didn't work")
    

def asset_accoutrements(request, asset, user, annotation_form):
    global_annotation = asset.global_annotation(user, auto_create=False)
    if global_annotation:
        global_annotation_form = GlobalAnnotationForm(instance=global_annotation, prefix="annotation")
    else:
        global_annotation_form = GlobalAnnotationForm(prefix="annotation")

    tags = calculate_cloud(
        Tag.objects.usage_for_queryset(
            asset.sherdnote_set.all(), counts=True))

    user_tags = calculate_cloud(
        Tag.objects.usage_for_queryset(
            user.sherdnote_set.filter(
                asset__course=request.course
                ), counts=True))

    comments = Comment and Comment.objects.for_model(asset) or None

    discussions = Clumper(DiscussionIndex.with_permission(
            request,
            #order, to be easily groupable by discussion
            DiscussionIndex.objects.filter(asset=asset).order_by('-modified')
            ), group_by='discussion')

    return {
        'asset': asset,
        'comments': comments,
        'global_annotation': global_annotation,
        'tags': tags,
        'space_viewer':user,
        'user_tags': user_tags,
        'annotation_form': annotation_form,
        'global_annotation_form': global_annotation_form,
        'discussions' : discussions
        }
    


@login_required
def asset_workspace(request, asset_id):
    try:
        asset = Asset.objects.get(pk=asset_id, course=request.course)
    
        user = request.user
        if user.is_staff and request.GET.has_key('as'):
            user = get_object_or_404(User,username=request.GET['as'])

        rv = asset_accoutrements(request, asset, user, 
                               AnnotationForm(prefix="annotation"))
    
        return render_to_response('assetmgr/asset.html', rv, context_instance=RequestContext(request))
    except Asset.DoesNotExist:
        asset = Asset.objects.get(pk=asset_id)
        
        # the user is logged into the wrong class?
        rv = {}
        rv['switch_to'] = asset.course
        rv['switch_from'] = request.course
        rv['redirect'] = reverse('asset-view', args=[asset_id])
        return render_to_response('assetmgr/asset_not_found.html', rv, context_instance=RequestContext(request))
    
    raise Http404()   


def asset_workspace_courselookup(asset_id=None):
    """lookup function corresponding to asset_workspace
    if an asset is being requested then we can guess the course
    """
    if asset_id:
        return Asset.objects.get(pk=asset_id).course

AUTO_COURSE_SELECT[asset_workspace] = asset_workspace_courselookup



from django.http import HttpResponseForbidden

from djangosherd.views import create_annotation
from djangosherd.views import delete_annotation
from djangosherd.views import edit_annotation
from djangosherd.views import annotation_dispatcher
from djangosherd.views import AnnotationForm
from djangosherd.views import GlobalAnnotationForm

@login_required
@allow_http("POST")
def create_annotations_container(request, asset_id):
    """
    delegate to djangosherd view and redirect back to asset workspace

    but first, stuff a range into the request (until sky's frontend
    comes in) and get the annotation context from the url
    """
    asset = get_object_or_404(Asset, pk=asset_id,
                              course=request.course)

    form = request.POST.copy()
    form['annotation-context_pk'] = asset_id
    request.POST = form

    form = request.GET.copy()
    form['annotation-next'] = reverse('asset-view', args=[asset_id])
    request.GET = form

    response = create_annotation(request)

    return response


@allow_http("GET", "POST", "DELETE")
def annotationview(request, asset_id, annot_id):

    user = request.user
    if user.is_staff and request.GET.has_key('as'):
        user = get_object_or_404(User,username=request.GET['as'])

    try:
        annotation = SherdNote.objects.get(pk=annot_id, 
                                       asset=asset_id,
                                       asset__course=request.course)
    
        if request.method in ("DELETE", "POST"):
            if request.method == "DELETE":
                redirect_to = reverse('asset-view', args=[asset_id])
            elif request.method == "POST":
                redirect_to = '.'
    
            form = request.GET.copy()
            form['next'] = redirect_to
            request.GET = form
            return annotation_dispatcher(request, annot_id)
    
        asset = annotation.asset
    
        global_annotation = asset.global_annotation(user, auto_create=False)
    
        if global_annotation == annotation:
            return HttpResponseRedirect(
                '%s#whole-form' % reverse('asset-view', args=[asset_id]))
    
        rv = asset_accoutrements(request, annotation.asset, user, 
                                 AnnotationForm(instance=annotation, prefix="annotation")
                                 )
        rv['annotation'] = annotation
        rv['readonly'] = (annotation.author != request.user)
        
        return render_to_response('assetmgr/asset.html', rv, context_instance=RequestContext(request))

    except SherdNote.DoesNotExist:
        annotation = get_object_or_404(SherdNote,
                                       pk=annot_id, 
                                       asset=asset_id)
        
        # the user is logged into the wrong class?
        rv = {}
        rv['switch_to'] = annotation.asset.course
        rv['switch_from'] = request.course
        rv['redirect'] = reverse('annotation-form', args=[asset_id, annot_id])
        
        return render_to_response('assetmgr/asset_not_found.html', rv, context_instance=RequestContext(request))

@rendered_with('assetmgr/browse_sources.html')
def browse_sources(request):
    c = request.course

    user = request.user
    if user.is_staff and request.GET.has_key('as'):
        user = get_object_or_404(User,username=request.GET['as'])

    archives = []
    upload_archive = None
    for a in c.asset_set.archives().order_by('title'):
        archive = a.sources['archive']
        thumb = a.sources.get('thumb',None)
        description = a.metadata().get('description','')
        uploader = a.metadata().get('upload', 0)
        
        archive_context = {
            "id":a.id,
            "title":a.title,
            "thumb":(None if not thumb else {"id":thumb.id, "url":thumb.url}),
            "archive":{"id":archive.id, "url":archive.url},
            #is description a list or a string?
            "metadata": (description[0] if hasattr(description,'append') else description)
        }
        
        if (uploader[0] if hasattr(uploader,'append') else uploader):
            upload_archive = archive_context
        else:
            archives.append(archive_context)
        
    archives.sort(key=operator.itemgetter('title'))
        
    rv = {"archives":archives,
          "upload_archive": upload_archive,
          "is_faculty":c.is_faculty(user),
          "space_viewer":user,
          'newsrc':request.GET.get('newsrc', ''),
          'can_upload': course_details.can_upload(request.user, request.course),
          'upload_service': getattr(settings,'UPLOAD_SERVICE',None),
          "help_browse_sources": UserSetting.get_setting(user, "help_browse_sources", True),
          "help_no_sources": UserSetting.get_setting(user, "help_no_sources", True),
          'msg': request.GET.get('msg', '')
          }
    if not rv['archives']:
        rv['faculty_assets'] = [a for a in Asset.objects.filter(c.faculty_filter).order_by('added')
                                if a not in rv['archives'] ]

    if getattr(settings,'DJANGOSHERD_FLICKR_APIKEY',None):
        # MUST only contain string values for now!! 
        # (see templates/assetmgr/bookmarklet.js to see why or fix)
        rv['bookmarklet_vars'] = {'flickr_apikey':settings.DJANGOSHERD_FLICKR_APIKEY }
        
    
    return rv

def source_redirect(request):
    url = request.GET.get('url',None)
    if not url:
        url = reverse('browse-sources')
    else:
        source = None
        try:
            source = Source.objects.get(primary=True, label='archive', url=url, asset__course=request.course)
        except Source.DoesNotExist:
            return HttpResponseForbidden("You can only redirect to an archive url")
        special = getattr(settings,'SERVER_ADMIN_SECRETKEYS',{})
        for server in special.keys():
            if url.startswith(server):
                url = source_specialauth(request,url,special[server])
                continue
        if url == source.url:
            return HttpResponseRedirect(source.url_processed(request))
    return HttpResponseRedirect(url)

        
def source_specialauth(request,url,key):
    import hmac, hashlib, datetime
    
    nonce = '%smthc' % datetime.datetime.now().isoformat()
    redirect_back = "%s?msg=upload" % (request.build_absolute_uri(reverse('explore')))
    username = request.user.username
    return '%s?set_course=%s&as=%s&redirect_url=%s&nonce=%s&hmac=%s' % (
        url,
        request.course.group.name,
        username,
        urllib.quote(redirect_back),
        nonce,
        hmac.new(key,
                 '%s:%s:%s' % (username,redirect_back,nonce),
                 hashlib.sha1
                 ).hexdigest()
        )

def asset_json(request, asset_id):
    asset = get_object_or_404(Asset,pk=asset_id)
    asset_key = 'x_%s' % asset.pk
    annotations = [{
            'asset_key':asset_key,
            'range1':None,
            'range2':None,
            'annotation':None,
            'id':'asset-%s' % asset.pk,
            'asset_id': asset.pk,
            }]
    
    if request.GET.has_key('annotations'):
        # @todo: refactor this serialization into a common place.
        def author_name(request, annotation, key):
            if not annotation.author_id:
                return None
            return 'author_name',get_public_name(annotation.author, request)
        for ann in asset.sherdnote_set.filter(range1__isnull=False):
            annotations.append( ann.sherd_json(request, 'x', ('title','author','tags',author_name,'body') ) )

    #we make assets plural here to be compatible with the project JSON structure
    data = {'assets': {asset_key:asset.sherd_json(request)},
            'annotations':annotations,
            'type':'asset',
            }
    return HttpResponse(simplejson.dumps(data, indent=2),
                        mimetype='application/json')

