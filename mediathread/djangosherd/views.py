import json
from json import JSONDecodeError

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseForbidden, \
    HttpResponseRedirect
from django.shortcuts import get_object_or_404
from djangohelpers.lib import allow_http

from mediathread.djangosherd.models import Asset, SherdNote, NULL_FIELDS
from mediathread.projects.models import ProjectNote, Project
from mediathread.taxonomy.views import update_vocabulary_terms


formfields = "tags title range1 range2 body annotation_data".split()
annotationfields = set("title range1 range2".split())


def is_clipping(data):
    clipping = False
    for field in NULL_FIELDS:
        if field in data:
            clipping = True
    return clipping


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

    clipping = is_clipping(data)

    assert clipping
    assert annotationfields.intersection(data)
    # ^^ the model will take care of the edge case

    annotation = SherdNote(**data)
    annotation.save()

    update_vocabulary_terms(request, annotation)

    # need to create global annotation if it doesn't exist already
    # so it appears in the user's list
    asset.global_annotation(annotation.author, auto_create=True)

    project_id = request.POST.get('project', None)
    if project_id:
        project = get_object_or_404(Project, id=project_id)
        ProjectNote.objects.create(project=project, annotation=annotation)

    if request.is_ajax():
        response = {'asset': {'id': asset.id},
                    'annotation': {'id': annotation.id}}
        return HttpResponse(json.dumps(response),
                            content_type="application/json")
    else:
        # new annotations should redirect 'back' to the asset
        # at the endpoint of the last annotation
        # so someone can create a new annotation ~lizday
        url_fragment = ''
        if annotation.range2:
            url_fragment = '#start=%s' % str(annotation.range2)

        next_url = annotation.asset.get_absolute_url() + url_fragment
        redirect_to = request.GET.get('next', next_url)

        return HttpResponseRedirect(redirect_to)


@login_required
def delete_annotation(request, annot_id):
    annotation = get_object_or_404(SherdNote, pk=annot_id)

    if annotation.author != request.user:
        return HttpResponseForbidden()

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
                            content_type="application/json")
    else:
        redirect_to = request.GET.get('next', '.')
        return HttpResponseRedirect(redirect_to)


@login_required
def update_annotation(request, annotation):
    if len(request.POST.keys()) > 0:
        form = dict(
            (key[len('annotation-'):], val)
            for key, val in request.POST.items()
            if key.startswith('annotation-')
        )
    else:
        # Try to load the data from the body as JSON, if it's not
        # included as form data.
        try:
            form = json.loads(request.body)
        except JSONDecodeError:
            form = {}

    if form.get('range1') or form.get('range2'):
        assert not annotation.is_null()

    for field in formfields:
        if field not in form:
            continue
        default = None
        if field == 'tags':
            default = ''

        setattr(
            annotation, field,
            form[field] or default)

    annotation.save()

    update_vocabulary_terms(request, annotation)
