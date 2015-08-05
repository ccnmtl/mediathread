from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from djangohelpers.lib import allow_http, rendered_with
from mediathread.mixins import faculty_only
from mediathread.taxonomy.models import VocabularyForm, Vocabulary, TermForm, \
    Term, TermRelationship


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


def update_vocabulary_terms(request, content_object):
    term_ids = request.POST.getlist('vocabulary')

    # Retrieve concepts/terms that this object is currently associated with
    associations = TermRelationship.objects.get_for_object(content_object)

    # Remove any unmentioned associations
    for a in associations:
        if (str(a.term.id) not in term_ids):
            a.delete()

    content_type = ContentType.objects.get_for_model(content_object)
    for term_id in term_ids:
        term = Term.objects.get(id=term_id)
        TermRelationship.objects.get_or_create(
            term=term,
            content_type=content_type,
            object_id=content_object.id)
