from django import forms
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.http import HttpResponseForbidden
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404

from djangosherd.models import Asset, SherdNote
from djangosherd.models import NULL_FIELDS
from tagging.models import Tag
from tagging.utils import calculate_cloud

from djangohelpers.lib import allow_http
from djangohelpers.lib import rendered_with

from assetmgr.lib import annotated_by,get_active_filters

from courseaffils.lib import in_course_or_404

import simplejson
from random import choice
from string import letters
import urllib2
from django.utils.http import urlquote  as django_urlquote

formfields = "tags title range1 range2 body annotation_data".split()
annotationfields = set("title range1 range2".split())

class AnnotationForm(forms.ModelForm):
    body = forms.CharField(label='My Clip Notes', widget=forms.widgets.Textarea(attrs={'rows':7, 'cols':51}) )
    range1 = forms.FloatField(widget=forms.widgets.HiddenInput,initial=0)
    range2 = forms.FloatField(widget=forms.widgets.HiddenInput,initial=0)
    annotation_data = forms.CharField(widget=forms.widgets.HiddenInput)
    tags = forms.CharField(label="My Clip Tags", help_text="<span class='helptext'>Use commas between tags.</span>")
    title = forms.CharField(label="My Clip Title")
    class Meta:
        model = SherdNote
        exclude = ('author', 'asset')

class GlobalAnnotationForm(forms.ModelForm):
    body = forms.CharField(label='My Item Notes', widget=forms.widgets.Textarea(attrs={'rows':7, 'cols':51}) )
    tags = forms.CharField(label='My Item Tags', help_text="<span class='helptext'>For multi-word tags, use underscores. Use commas to separate tags.<br />Example: Vietnam_War, Fall_of_Saigon</span>")
    class Meta:
        model = SherdNote
        exclude = ('annotation_data', 'author', 'asset', 'range1', 'range2', 'title')

@login_required
@allow_http("POST")
def create_annotation(request):
    asset = get_object_or_404(Asset,
                              pk=request.POST['annotation-context_pk'])

    form = dict((key[len('annotation-'):], val) for key, val in request.POST.items()
                if key.startswith('annotation-'))
        
    del form['context_pk']

    data = {'author': request.user,
            'asset': asset}

    for field in formfields:
        if form.get(field) != '':
            data[field] = form[field]

    clipping = False
    for field in NULL_FIELDS:
        if field in data:
            clipping = True
                
    assert clipping
    assert annotationfields.intersection(data)
    # ^^ the model will take care of the edge case

    annotation = SherdNote(**data)
    annotation.save()

    #need to create global annotation if it doesn't exist already
    #so it appears in the user's list
    asset.global_annotation(annotation.author, auto_create=True)

    #new annotations should redirect 'back' to the asset
    # at the endpoint of the last annotation
    # so someone can create a new annotation ~lizday
    url_fragment = ''
    if annotation.range2:
        url_fragment = '#start=%s' % str(annotation.range2)

    redirect_to = request.GET.get('next',
                                  annotation.asset.get_absolute_url() + url_fragment  )
    return HttpResponseRedirect(redirect_to)

@allow_http("POST", "DELETE")
def annotation_dispatcher(request, annot_id):
    if request.method == "DELETE":
        return delete_annotation(request, annot_id)
    if request.method == "POST":
        return edit_annotation(request, annot_id)
    #if request.method == "GET":
    #    return view_annotation(request, annot_id)

@login_required
def delete_annotation(request, annot_id):
    annotation = get_object_or_404(SherdNote, pk=annot_id)

    if annotation.author != request.user:
        return HttpResponseForbidden

    annotation.delete()
    redirect_to = request.GET.get('next', '/')
    return HttpResponseRedirect(redirect_to)

@login_required
def edit_annotation(request, annot_id):
    annotation = get_object_or_404(SherdNote, pk=annot_id)

    if annotation.author != request.user:
        return HttpResponseForbidden("forbidden")

    form = dict((key[len('annotation-'):], val) for key, val in request.POST.items()
                if key.startswith('annotation-'))

    # don't let a global annotation turn into a clip, or v.v.
    if form.get('range1') or form.get('range2'):
        assert not annotation.is_null()
    else:
        assert annotation.is_null()

    for field in formfields:
        if field not in form: continue
        default = None
        if field == 'tags': default = ''
        setattr(annotation, field,
                form[field] or default)
    annotation.save()

    if request.is_ajax():
        response = dict(title=annotation.title,
                        tags=annotation.tags,
                        body=annotation.body)
        response = simplejson.dumps(response)
        return HttpResponse(response, mimetype="application/json")
    
    redirect_to = request.GET.get('next', '.')
    return HttpResponseRedirect(redirect_to)

@login_required
@rendered_with('assetmgr/asset_table.html')
def annotations_collection_fragment(request,username=None):
    """username is WAY overloaded
     username='none' : just give me the selection menu
     username=None : give me all assets for the class
     username=<username> : all username assets
    """
    rv = {'space_viewer':request.user,
          'space_owner':False, #indicates we want the whole class (None is no one)
          'page_in_edit_mode': request.GET.has_key('edit_mode'),
          }
    if username != 'none':
        if username:
            rv['space_owner'] = in_course_or_404(username, request.course)
            #assets = annotated_by(Asset.objects.filter(course=request.course),
            #                      space_owner)
            note_query = rv['space_owner'].sherdnote_set.filter(asset__course=request.course)
        else:
            #assets = Asset.objects.filter(course=request.course)
            note_query = SherdNote.objects.filter(asset__course=request.course)

        rv['tags'] =  calculate_cloud(Tag.objects.usage_for_queryset(note_query, counts=True))

        #all_tags.sort(lambda a,b:cmp(a.name.lower(),b.name.lower()))
        #all_tags = calculate_cloud(all_tags)
    
        filter_by = ('tag','modified')

        for fil in filter_by:
            filter_value = request.GET.get(fil)
            if filter_value:
                s_filter = getattr(SherdNote.objects,'%s_filter'%fil)
                note_query = s_filter(filter_value,note_query)

        #until asset_table.html can work off the notes objects instead of the assets list
        rv['assets'] = Asset.objects.filter(id__in = note_query.values_list('asset',flat=True))

        rv['active_filters'] = get_active_filters(request)
        rv['dates'] = (('today','today'),
                       ('yesterday','yesterday'),
                       ('lastweek','within the last week'),
                       )
    
    return rv

@rendered_with('djangosherd/iframe_annotation.html')
def annotation_iframe_view(request, asset_id, annot_id):
    annotation = get_object_or_404(SherdNote,
                                   pk=annot_id, asset=asset_id)

    #during testing and before SC wrapper
    if annotation.author != request.user:
        return HttpResponseForbidden("forbidden")

    readonly = True
    
    asset = annotation.asset
    course = asset.course

    global_annotation = asset.global_annotation(annotation.author)

    if global_annotation == annotation:
        return HttpResponseRedirect(
            reverse('asset-view', args=[asset_id]))

    return {
        'asset': asset,
        'course': course,
        'annotation': annotation,
        'readonly': readonly,
        }

def annotation_json(request, annot_id):
    ann = get_object_or_404(SherdNote,pk=annot_id)
    rand = ''.join([choice(letters) for i in range(5)])

    data = {'assets':dict([('%s_%s' % (rand,ann.asset.pk),
                            ann.asset.sherd_json(request))]),
            #should correspond to same format in project.views.project_json
            'annotations':[{
                'asset_key':'%s_%s' % (rand,ann.asset_id),
                'id':ann.pk,
                'range1':ann.range1,
                'range2':ann.range2,
                'annotation':ann.annotation(),
                'metadata':{
                    'title':ann.title,
                    'author':{'id':ann.author_id,
                              #'name':ann.author.get_full_name(),
                              },
                    },
                }],
            'type':'annotation',
            }
                          
    return HttpResponse(simplejson.dumps(data, indent=2),
                        mimetype='application/json')


def final_cut_pro_xml(request, annot_id):
    "support for http://developer.apple.com/mac/library/documentation/AppleApplications/Reference/FinalCutPro_XML/Topics/Topics.html"
    try:
        from xmeml import VideoSequence
        #http://github.com/ccnmtl/xmeml
        ann = get_object_or_404(SherdNote, pk=annot_id)
        xmeml = ann.asset.sources.get('xmeml', None)
        if xmeml is None:
            return HttpResponse("Not Found: This annotation's asset does not have a Final Cut Pro source XML associated with it", status=404)
        f = urllib2.urlopen(xmeml.url)
        assert f.code == 200
        v = VideoSequence(xml_string=f.read())
        clip = v.clip(ann.range1, ann.range2 ,units='seconds')
        xmldom,dumb_uuid = v.clips2dom([clip])
        res = HttpResponse(xmldom.toxml(), mimetype='application/xml')
        res['Content-Disposition'] = 'attachment; filename="%s.xml"' % ann.title
        return res

    except ImportError:
        return HttpResponse('Not Implemented: No Final Cut Pro Xmeml support', status=503)

