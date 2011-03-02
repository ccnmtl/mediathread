from django.contrib.auth.decorators import login_required
from django.core import serializers
from django.core.urlresolvers import reverse
from django.db import transaction
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response

from django.contrib.contenttypes.models import ContentType
from threadedcomments import ThreadedComment
from structuredcollaboration.models import Collaboration
from mediathread_main.clumper import Clumper

from django.conf import settings

from django.shortcuts import get_object_or_404
from django.db import models

import simplejson

import re

Asset = models.get_model('assetmgr','asset')
Source = models.get_model('assetmgr','source')
SherdNote = models.get_model('djangosherd','sherdnote')
DiscussionIndex = models.get_model('djangosherd','discussionindex')
User = models.get_model('auth','user')
from djangosherd.views import AnnotationForm, GlobalAnnotationForm

Comment = models.get_model('comments','comment')

from djangohelpers.lib import rendered_with
from djangohelpers.lib import allow_http

from assetmgr.lib import filter_by,get_active_filters

from tagging.models import Tag
from tagging.utils import calculate_cloud
from courseaffils.lib import in_course_or_404, AUTO_COURSE_SELECT



OPERATION_TAGS = ('jump','title','noui','v','share','as','set_course')
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


@login_required
@allow_http("GET", "POST")
def add_view(request):
    if request.method == "POST":
        return add_asset(request)

    asset = Asset.objects.get_by_args(request.GET,
                                      asset__course=request.course)

    if asset:
        return HttpResponseRedirect(
            reverse('asset-view', args=[asset.id]))
    elif asset is None:
        return mock_analysis_space(request)
    else: #asset is False with no good args
        #no arguments so /save space
        return asset_addform(request)

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

@rendered_with('assetmgr/asset_addform.html')
def asset_addform(request):
    from supported_archives import all 
    return {
        'asset_request':request.GET,
        'supported_archives':all,
        }

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
    if user.is_staff and request.REQUEST.has_key('as'):
        user = get_object_or_404(User,username=request.REQUEST['as'])

    if not request.course.is_true_member(user):
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
        asset = Asset(title=title[:1020], #max title length
                      course=request.course,
                      author=user)
        asset.save()
        for source in sources_from_args(request, asset).values():
            source.save()

        transaction.commit()
        if len(metadata):
            asset.metadata_blob = simplejson.dumps(metadata)
            asset.save()
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
            annotationcontainerview(request, asset.pk)
            transaction.commit()

        asset_url = reverse('asset-view', args=[asset.id])

        #for bookmarklet mass-adding
        if request.REQUEST.get('noui','').startswith('postMessage'):
            return render_to_response('assetmgr/interface_iframe.html',
                                      {'message': '%s|%s' % (request.build_absolute_uri(asset_url),
                                                             request.REQUEST['noui']),
                                       })
        elif not request.is_ajax():
            return HttpResponseRedirect(asset_url)
        else:
            return HttpResponse(serializers.serialize('json',asset),
                                mimetype="application/json")
    else:
        #we'll make it here if someone doesn't submit
        #any primary_labels as arguments
        raise AssertionError("something didn't work")


@rendered_with('assetmgr/asset_container.html')
def container_view(request):
    "for all class assets view at /asset/ "
    #extra() is case-insensitive order hack
    #http://scottbarnham.com/blog/2007/11/20/case-insensitive-ordering-with-django-and-postgresql/
    assets = [a for a in Asset.objects.filter(course=request.course).extra(
            select={'lower_title': 'lower(title)'}
            ).order_by('lower_title')
              if a not in request.course.asset_set.archives()]

    from tagging.models import Tag
    all_tags = Tag.objects.usage_for_queryset(
        SherdNote.objects.filter(
            asset__course=request.course),
        counts=True)
    all_tags.sort(lambda a,b:cmp(a.name.lower(),b.name.lower()))
    all_tags = calculate_cloud(all_tags)

    for fil in filter_by:
        filter_value = request.GET.get(fil)
        if filter_value:
            assets = [asset for asset in assets
                      if filter_by[fil](asset, filter_value)]

    active_filters = get_active_filters(request)

    return {
        'assets':assets,
        'tags': all_tags,
        'active_filters': active_filters,
        'space_viewer':request.user,
        'space_owner':None,
        'is_faculty':request.course.is_faculty(request.user),
        }

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
@rendered_with('assetmgr/asset.html')
def asset_workspace(request, asset_id):
    asset = get_object_or_404(Asset, pk=asset_id,
                              course=request.course)

    user = request.user
    if user.is_staff and request.GET.has_key('as'):
        user = get_object_or_404(User,username=request.GET['as'])

    return asset_accoutrements(request, asset, user, 
                               AnnotationForm(prefix="annotation"))

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
def annotationcontainerview(request, asset_id):
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


@rendered_with('assetmgr/asset.html')
@allow_http("GET", "POST", "DELETE")
def annotationview(request, asset_id, annot_id):
    annotation = get_object_or_404(SherdNote,
                                   pk=annot_id, asset=asset_id,
                                   asset__course=request.course)

    user = request.user
    if user.is_staff and request.GET.has_key('as'):
        user = get_object_or_404(User,username=request.GET['as'])

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

    return rv

@rendered_with('assetmgr/explore.html')
def archive_explore(request):
    c = request.course

    user = request.user
    if user.is_staff and request.GET.has_key('as'):
        user = get_object_or_404(User,username=request.GET['as'])

    rv = {"archives":c.asset_set.archives().order_by('title'),
          "is_faculty":c.is_faculty(user),
          "space_viewer":user,
          }
    if not rv['archives']:
        rv['faculty_assets'] = [a for a in Asset.objects.filter(c.faculty_filter).order_by('added')
                                if a not in rv['archives'] ]

    if getattr(settings,'DJANGOSHERD_FLICKR_APIKEY',None):
        # MUST only contain string values for now!! 
        # (see templates/assetmgr/bookmarklet.js to see why or fix)
        rv['bookmarklet_vars'] = {'flickr_apikey':settings.DJANGOSHERD_FLICKR_APIKEY }
    return rv

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
        for ann in asset.sherdnote_set.filter(range1__isnull=False):
            annotations.append( ann.sherd_json(request, 'x', ('title','author','tags','author_name','body') ) )
            
    data = {'assets':dict( [(asset_key,
                             asset.sherd_json(request)
                             )] ),
            'annotations':annotations,
            'type':'asset',
            }
    return HttpResponse(simplejson.dumps(data, indent=2),
                        mimetype='application/json')

