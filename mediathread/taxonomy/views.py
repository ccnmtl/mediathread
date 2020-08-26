from django.contrib.auth.decorators import login_required
from djangohelpers.lib import allow_http, rendered_with
from mediathread.mixins import attach_course_request, faculty_only
from mediathread.taxonomy.models import VocabularyForm, Vocabulary, TermForm, \
    Term, TermRelationship


@login_required
@attach_course_request
@allow_http("GET")
@rendered_with('taxonomy/taxonomy.html')
@faculty_only
def taxonomy_workspace(request):
    vocabularies = Vocabulary.objects.filter(course=request.course)
    for v in vocabularies:
        v.form = VocabularyForm(instance=v)

    form = VocabularyForm(initial={'name': 'initial',
                                   'course': request.course})

    return {
        'vocabularies': vocabularies,
        'vocabulary_form': form,
        'course': request.course,
        'term_form': TermForm(),
    }


def update_vocabulary_terms(request, note, term_ids=None):
    if not term_ids:
        term_ids = request.POST.getlist('vocabulary')

    # Retrieve concepts/terms that this object is currently associated with
    associations = TermRelationship.objects.filter(sherdnote=note)

    # Remove any unmentioned associations
    for a in associations:
        if (str(a.term.id) not in term_ids):
            a.delete()

    for term_id in term_ids:
        term = Term.objects.get(id=term_id)
        TermRelationship.objects.get_or_create(
            term=term, sherdnote=note)
