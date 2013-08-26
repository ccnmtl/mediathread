from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from djangohelpers.lib import allow_http, rendered_with
from mediathread.main.decorators import faculty_only
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
    concepts = dict((key[len('vocabulary-'):], request.POST.getlist(key))
                    for key, val in request.POST.items()
                    if key.startswith('vocabulary-'))

    # Retrieve concepts/terms that this object is currently associated with
    associations = TermRelationship.objects.get_for_object(content_object)

    # Remove any unmentioned associations
    for a in associations:
        vocabulary_id = str(a.term.vocabulary.id)
        term_id = str(a.term.id)
        if (not vocabulary_id in concepts or
                not term_id in concepts[vocabulary_id]):
            a.delete()

    content_type = ContentType.objects.get_for_model(content_object)
    for name, terms in concepts.items():
        for term_id in concepts[name]:
            term = Term.objects.get(id=int(term_id))
            TermRelationship.objects.get_or_create(
                term=term,
                content_type=content_type,
                object_id=content_object.id)
