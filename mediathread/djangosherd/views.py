from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseForbidden, \
    HttpResponseRedirect
from django.shortcuts import get_object_or_404
from djangohelpers.lib import allow_http
from mediathread.djangosherd.models import Asset, SherdNote, NULL_FIELDS
from mediathread.taxonomy.views import update_vocabulary_terms
import json

formfields = "tags title range1 range2 body annotation_data".split()
annotationfields = set("title range1 range2".split())


@login_required
@allow_http("POST")
def create_annotation(request):
    asset = get_object_or_404(Asset,
                              pk=request.POST['annotation-context_pk'])

    form = dict((key[len('annotation-'):], val)
                for key, val in request.POST.items()
                if key.startswith('annotation-'))

    del form['context_pk']

    data = {'author': request.user, 'asset': asset}

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

    update_vocabulary_terms(request, annotation)

    #need to create global annotation if it doesn't exist already
    #so it appears in the user's list
    asset.global_annotation(annotation.author, auto_create=True)

    if request.is_ajax():
        response = {'asset': {'id': asset.id},
                    'annotation': {'id': annotation.id}}
        return HttpResponse(json.dumps(response),
                            mimetype="application/json")
    else:
        #new annotations should redirect 'back' to the asset
        # at the endpoint of the last annotation
        # so someone can create a new annotation ~lizday
        url_fragment = ''
        if annotation.range2:
            url_fragment = '#start=%s' % str(annotation.range2)

        next_url = annotation.asset.get_absolute_url() + url_fragment
        redirect_to = request.GET.get('next', next_url)

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
        response = {'asset': {'id': annotation.asset_id},
                    'annotation': {'id': annotation.id}}
        return HttpResponse(json.dumps(response),
                            mimetype="application/json")
    else:
        redirect_to = request.GET.get('next', '.')
        return HttpResponseRedirect(redirect_to)


@login_required
def update_annotation(request, annotation):

    form = dict((key[len('annotation-'):], val)
                for key, val in request.POST.items()
                if key.startswith('annotation-'))

    ## @todo -- figure out how the clipform gets into the
    # annotations.mustache form
    # don't let a global annotation turn into a clip, or v.v.
    if form.get('range1') or form.get('range2'):
        assert not annotation.is_null()
    else:
        assert annotation.is_null()

    for field in formfields:
        if field not in form:
            continue
        default = None
        if field == 'tags':
            default = ''
        setattr(annotation, field,
                form[field] or default)

    annotation.save()

    update_vocabulary_terms(request, annotation)
