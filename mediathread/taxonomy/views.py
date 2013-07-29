from courseaffils.lib import in_course_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404
from djangohelpers.lib import allow_http, rendered_with
from mediathread.main.decorators import ajax_required, faculty_only
from mediathread.taxonomy.models import VocabularyForm, Vocabulary, TermForm, \
    Term
import simplejson


@login_required
@allow_http("GET")
@rendered_with('taxonomy/taxonomy.html')
@faculty_only
def taxonomy_workspace(request):
    vocabularies = Vocabulary.objects.get_for_object(request.course)
    for v in vocabularies:
        v.form = VocabularyForm(instance=v)

    course_type = ContentType.objects.get_for_model(request.course)
    form = VocabularyForm(initial={'name': 'initial',
                                   'content_type': course_type,
                                   'object_id': request.course.id})

    return {
        'vocabularies': vocabularies,
        'vocabulary_form': form,
        'course': request.course,
        'course_type': course_type,
        'term_form': TermForm(),
    }


@login_required
@allow_http("POST")
@rendered_with('taxonomy/taxonomy_workspace.html')
@faculty_only
def vocabulary_create(request):
    in_course_or_404(request.user.username, request.course)

    form = VocabularyForm(request.POST)
    if form.is_valid():
        form.save()
        return HttpResponseRedirect(reverse('taxonomy-workspace', args=[]))

    return {
        'vocabulary_form': form,
        'course': request.course,
        'course_type': ContentType.objects.get_for_model(request.course)
    }


@login_required
@allow_http("POST")
@ajax_required
@faculty_only
def vocabulary_save(request, vocabulary_id):
    in_course_or_404(request.user.username, request.course)

    vocabulary = get_object_or_404(Vocabulary, id=vocabulary_id)
    form = VocabularyForm(request.POST, instance=vocabulary)
    if form.is_valid():
        form.save()
        data = {'status': 'success'}
    else:
        data = {'status': 'error'}

    json_stream = simplejson.dumps(data, indent=2)
    return HttpResponse(json_stream, mimetype='application/json')


@login_required
@allow_http("POST")
@ajax_required
@faculty_only
def vocabulary_delete(request, vocabulary_id):
    in_course_or_404(request.user.username, request.course)

    vocabulary = get_object_or_404(Vocabulary, id=vocabulary_id)
    vocabulary.delete()

    return HttpResponseRedirect(reverse('taxonomy-workspace', args=[]))


@login_required
@allow_http("POST")
@ajax_required
@faculty_only
def term_create(request, vocabulary_id):
    in_course_or_404(request.user.username, request.course)

    vocabulary = get_object_or_404(Vocabulary, id=vocabulary_id)
    display_name = request.POST.get('display_name', '')
    description = request.POST.get('description', '')

    data = {}
    if not len(display_name):
        data['status'] = 'error'
    else:
        data['status'] = 'success'
        term = Term(display_name=display_name,
                    description=description,
                    vocabulary=vocabulary)
        term.save()
        data['term'] = term.to_json()

    json_stream = simplejson.dumps(data, indent=2)
    return HttpResponse(json_stream, mimetype='application/json')


@login_required
@allow_http("POST")
@ajax_required
@faculty_only
def term_delete(request, term_id):
    in_course_or_404(request.user.username, request.course)

    term = get_object_or_404(Term, id=term_id)
    term.delete()

    data = {'status': 'success'}
    json_stream = simplejson.dumps(data, indent=2)
    return HttpResponse(json_stream, mimetype='application/json')
