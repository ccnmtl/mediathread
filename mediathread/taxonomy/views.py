from courseaffils.lib import in_course_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from djangohelpers.lib import allow_http, rendered_with
from mediathread.taxonomy.models import VocabularyForm, Vocabulary, TermForm


@login_required
@allow_http("GET")
@rendered_with('taxonomy/taxonomy_workspace.html')
def taxonomy_workspace(request):
    if not request.course.is_faculty(request.user):
        return HttpResponseForbidden("forbidden")

    vocabularies = Vocabulary.objects.get_for_object(request.course)

    return {
        'vocabularies': vocabularies,
        'vocabulary_form': VocabularyForm(),
        'vocabulary_form2': VocabularyForm(instance=vocabularies[0]),
        'course': request.course,
        'course_type': ContentType.objects.get_for_model(request.course),
        'term_form': TermForm(),
    }


@login_required
@allow_http("POST")
@rendered_with('taxonomy/taxonomy_workspace.html')
def vocabulary_create(request):
    if not request.course.is_faculty(request.user):
        return HttpResponseForbidden("forbidden")

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
def vocabulary_delete(request, vocabulary_id):
    if not request.course.is_faculty(request.user):
        return HttpResponseForbidden("forbidden")

    in_course_or_404(request.user.username, request.course)

    vocabulary = get_object_or_404(Vocabulary, id=vocabulary_id)
    vocabulary.delete()

    return HttpResponseRedirect(reverse('taxonomy-workspace', args=[]))
