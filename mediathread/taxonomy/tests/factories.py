from courseaffils.models import Course
from django.contrib.contenttypes.models import ContentType
from mediathread.djangosherd.models import SherdNote
from mediathread.taxonomy.models import Vocabulary, Term, TermRelationship
from tastypie.test import ResourceTestCase


class TaxonomyTestCase(ResourceTestCase):
    fixtures = ['unittest_sample_course.json']

    def create_vocabularies(self, course, taxonomy):
        course_type = ContentType.objects.get_for_model(course)

        for name, terms in taxonomy.items():
            concept = Vocabulary(display_name=name,
                                 content_type=course_type,
                                 object_id=course.id)
            concept.save()
            for term_name in terms:
                term = Term(display_name=term_name,
                            vocabulary=concept)
                term.save()

    def create_term_relationship(self, content_object, term):
        # Add some tags to a few notes
        content_type = ContentType.objects.get_for_model(content_object)
        TermRelationship.objects.get_or_create(
            term=term,
            content_type=content_type,
            object_id=content_object.id)

    def setUp(self):
        super(TaxonomyTestCase, self).setUp()

        course = Course.objects.get(title="Sample Course")
        taxonomy = {
            'Shapes': ['Square', 'Triangle'],
            'Colors': ['Red', 'Blue', 'Green']
        }
        self.create_vocabularies(course, taxonomy)

        course = Course.objects.get(title="Alternate Course")
        taxonomy = {
            'Materials': ['Paper', 'Wood', 'Stone']
        }
        self.create_vocabularies(course, taxonomy)

        # test_instructor in Sample Course
        note = SherdNote.objects.get(title="Left Corner")
        term = Term.objects.get(name="square")
        self.create_term_relationship(note, term)
        term = Term.objects.get(name="red")
        self.create_term_relationship(note, term)

        # test_student_two in Sample Course
        note = SherdNote.objects.get(title="Nice Tie")
        term = Term.objects.get(name="square")
        self.create_term_relationship(note, term)

        # test_student_three in Alternate Course
        note = SherdNote.objects.get(title="Whole Item Selection",
                                     author__username='test_student_three')
        term = Term.objects.get(name="paper")
        self.create_term_relationship(note, term)
