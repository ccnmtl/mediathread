from django import forms
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.http import HttpResponseForbidden
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse

from djangosherd.models import Asset, SherdNote
from djangosherd.models import NULL_FIELDS

from tagging.models import Tag
from tagging.utils import calculate_cloud

from djangohelpers.lib import allow_http
from djangohelpers.lib import rendered_with

from courseaffils.lib import in_course_or_404, in_course,get_public_name
from mediathread_main import course_details

import simplejson
import re
from random import choice
from string import letters
from django.utils.http import urlquote  as django_urlquote

formfields = "tags title range1 range2 body annotation_data".split()
annotationfields = set("title range1 range2".split())

class AnnotationForm(forms.ModelForm):
    body = forms.CharField(label='Notes', widget=forms.widgets.Textarea(attrs={'rows':7, 'cols':51}) )
    range1 = forms.FloatField(widget=forms.widgets.HiddenInput,initial=0)
    range2 = forms.FloatField(widget=forms.widgets.HiddenInput,initial=0)
    annotation_data = forms.CharField(widget=forms.widgets.HiddenInput)
    tags = forms.CharField(label="Tag(s)", help_text="<span class='helptext'>Use commas between tags.</span>")
    title = forms.CharField(label="Title")
    class Meta:
        model = SherdNote
        exclude = ('author', 'asset')

    def __init__(self, *args, **kw):
        forms.ModelForm.__init__(self, *args, **kw)
        # second part of tag 'space' hack (see models.py::SherdNote.save)
        #to avoid 'American Revolution' being tagged as "American", "Revolution"
        if self.initial.get('tags','').startswith(','):
            self.initial['tags'] = self.initial['tags'][1:]

class GlobalAnnotationForm(forms.ModelForm):
    body = forms.CharField(label='My Item Notes', widget=forms.widgets.Textarea(attrs={'rows':7, 'cols':51}) )
    tags = forms.CharField(label='My Item Tags', help_text="<span class='helptext'>Use commas to separate tags. Example: tag 1, tag 2, tag 3</span>")
    class Meta:
        model = SherdNote
        exclude = ('annotation_data', 'author', 'asset', 'range1', 'range2', 'title')

    def __init__(self, *args, **kw):
        forms.ModelForm.__init__(self, *args, **kw)
        # second part of tag 'space' hack (see models.py::SherdNote.save)
        #to avoid 'American Revolution' being tagged as "American", "Revolution"
        if self.initial.get('tags','').startswith(','):
            self.initial['tags'] = self.initial['tags'][1:]

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

    if request.is_ajax():
        response = { 'asset': { 'id': asset.id }, 'annotation': { 'id': annotation.id } }
        return HttpResponse(simplejson.dumps(response), mimetype="application/json")
    else:
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
    
    update_annotation(request, annotation)

    if request.is_ajax():
        response = { 'asset': { 'id': annotation.asset_id }, 'annotation': { 'id': annotation.id } }
        return HttpResponse(simplejson.dumps(response), mimetype="application/json")
    else:
        redirect_to = request.GET.get('next', '.')
        return HttpResponseRedirect(redirect_to)
    
@login_required    
def update_annotation(request, annotation):
    
    form = dict((key[len('annotation-'):], val) for key, val in request.POST.items()
                if key.startswith('annotation-'))

    ## @todo -- figure out how the clipform gets into the annotations.mustache form
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
