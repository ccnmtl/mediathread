from courseaffils.models import Course
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from django.test.client import RequestFactory
from mediathread.djangosherd.models import SherdNote
from mediathread.taxonomy.models import Vocabulary, Term, TermRelationship
from mediathread.taxonomy.views import update_vocabulary_terms


class TaxonomyViewTest(TestCase):
    fixtures = ['unittest_sample_course.json']

    def setUp(self):
        # Every test needs access to the request factory.
        self.factory = RequestFactory()

        course = Course.objects.get(id=1)
        course_type = ContentType.objects.get_for_model(course)

        taxonomy = {
            'Shapes': ['Square', 'Triangle', 'Circle'],
            'Colors': ['Red', 'Blue', 'Green']
        }

        for name, terms in taxonomy.items():
            concept = Vocabulary(display_name=name,
                                 content_type=course_type,
                                 object_id=course.id)
            concept.save()
            for term_name in terms:
                term = Term(display_name=term_name,
                            vocabulary=concept)
                term.save()

    def test_simple_association(self):
        concept = Vocabulary.objects.get(display_name="Shapes")
        term = Term.objects.get(display_name="Square")
        post_data = {'vocabulary-%s' % str(concept.id): [str(term.id)]}

        sherd_note = SherdNote.objects.get(id=1)
        related_terms = TermRelationship.objects.get_for_object(sherd_note)
        self.assertEquals(len(related_terms), 0)

        request = self.factory.post('/', post_data)
        update_vocabulary_terms(request, sherd_note)

        related_terms = TermRelationship.objects.get_for_object(sherd_note)
        self.assertEquals(len(related_terms), 1)
        self.assertEquals(related_terms[0].term, term)
        self.assertEquals(related_terms[0].object_id, sherd_note.id)

    def test_removal(self):
        term = Term.objects.get(display_name="Square")

        sherd_note = SherdNote.objects.get(id=1)
        sherdnote_type = ContentType.objects.get_for_model(sherd_note)

        TermRelationship.objects.create(term=term,
                                        object_id=sherd_note.id,
                                        content_type=sherdnote_type)
        related_terms = TermRelationship.objects.get_for_object(sherd_note)
        self.assertEquals(len(related_terms), 1)

        request = self.factory.post('/', {})
        update_vocabulary_terms(request, sherd_note)

        related_terms = TermRelationship.objects.get_for_object(sherd_note)
        self.assertEquals(len(related_terms), 0)

    def test_removal_and_association(self):
        concept = Vocabulary.objects.get(display_name="Shapes")
        square = Term.objects.get(display_name="Square")
        circle = Term.objects.get(display_name="Circle")

        sherd_note = SherdNote.objects.get(id=1)
        sherdnote_type = ContentType.objects.get_for_model(sherd_note)

        TermRelationship.objects.create(term=square,
                                        object_id=sherd_note.id,
                                        content_type=sherdnote_type)
        related_terms = TermRelationship.objects.get_for_object(sherd_note)
        self.assertEquals(len(related_terms), 1)

        post_data = {'vocabulary-%s' % str(concept.id): [str(circle.id)]}
        request = self.factory.post('/', post_data)
        update_vocabulary_terms(request, sherd_note)

        related_terms = TermRelationship.objects.get_for_object(sherd_note)
        self.assertEquals(len(related_terms), 1)
        self.assertEquals(related_terms[0].term, circle)
        self.assertEquals(related_terms[0].object_id, sherd_note.id)

    def test_multiple_associations_and_removals(self):
        shapes = Vocabulary.objects.get(display_name="Shapes")
        square = Term.objects.get(display_name="Square")
        circle = Term.objects.get(display_name="Circle")

        colors = Vocabulary.objects.get(display_name="Colors")
        red = Term.objects.get(display_name='Red')
        blue = Term.objects.get(display_name='Blue')

        sherd_note = SherdNote.objects.get(id=1)
        sherdnote_type = ContentType.objects.get_for_model(sherd_note)

        TermRelationship.objects.create(term=square,
                                        object_id=sherd_note.id,
                                        content_type=sherdnote_type)
        TermRelationship.objects.create(term=red,
                                        object_id=sherd_note.id,
                                        content_type=sherdnote_type)
        related_terms = TermRelationship.objects.get_for_object(sherd_note)
        self.assertEquals(len(related_terms), 2)
        self.assertEquals(related_terms[0].term, square)
        self.assertEquals(related_terms[0].object_id, sherd_note.id)
        self.assertEquals(related_terms[1].term, red)
        self.assertEquals(related_terms[1].object_id, sherd_note.id)

        post_data = {
            'vocabulary-%s' % str(shapes.id): [str(circle.id)],
            'vocabulary-%s' % str(colors.id): [str(blue.id)],
        }
        request = self.factory.post('/', post_data)
        update_vocabulary_terms(request, sherd_note)

        related_terms = TermRelationship.objects.get_for_object(sherd_note)
        self.assertEquals(len(related_terms), 2)
        self.assertEquals(related_terms[0].term, circle)
        self.assertEquals(related_terms[0].object_id, sherd_note.id)
        self.assertEquals(related_terms[1].term, blue)
        self.assertEquals(related_terms[1].object_id, sherd_note.id)
