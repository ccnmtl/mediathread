# pylint: disable-msg=R0904
from django.contrib.contenttypes.models import ContentType
from django.test.client import RequestFactory
from django.test.testcases import TestCase

from mediathread.factories import AssetFactory, SherdNoteFactory, \
    MediathreadTestMixin
from mediathread.taxonomy.models import Vocabulary, Term, TermRelationship
from mediathread.taxonomy.views import update_vocabulary_terms


class TaxonomyViewTest(MediathreadTestMixin, TestCase):

    def setUp(self):
        self.setup_sample_course()
        self.factory = RequestFactory()

        taxonomy = {
            'Shapes': ['Square', 'Triangle', 'Circle'],
            'Colors': ['Red', 'Blue', 'Green']
        }
        self.create_vocabularies(self.sample_course, taxonomy)

        self.asset = AssetFactory(course=self.sample_course)
        self.note = SherdNoteFactory(
            asset=self.asset, author=self.student_one,
            title="Whole Item Selection", range1=116.25, range2=6.75)

    def test_simple_association(self):
        concept = Vocabulary.objects.get(display_name="Shapes")
        term = Term.objects.get(display_name="Square")
        post_data = {'vocabulary-%s' % str(concept.id): [str(term.id)]}

        related_terms = TermRelationship.objects.get_for_object(self.note)
        self.assertEquals(len(related_terms), 0)

        request = self.factory.post('/', post_data)
        update_vocabulary_terms(request, self.note)

        related_terms = TermRelationship.objects.get_for_object(self.note)
        self.assertEquals(len(related_terms), 1)
        self.assertEquals(related_terms[0].term, term)
        self.assertEquals(related_terms[0].object_id, self.note.id)

    def test_removal(self):
        term = Term.objects.get(display_name="Square")

        sherdnote_type = ContentType.objects.get_for_model(self.note)

        TermRelationship.objects.create(term=term,
                                        object_id=self.note.id,
                                        content_type=sherdnote_type)
        related_terms = TermRelationship.objects.get_for_object(self.note)
        self.assertEquals(len(related_terms), 1)

        request = self.factory.post('/', {})
        update_vocabulary_terms(request, self.note)

        related_terms = TermRelationship.objects.get_for_object(self.note)
        self.assertEquals(len(related_terms), 0)

    def test_removal_and_association(self):
        concept = Vocabulary.objects.get(display_name="Shapes")
        square = Term.objects.get(display_name="Square")
        circle = Term.objects.get(display_name="Circle")

        sherdnote_type = ContentType.objects.get_for_model(self.note)

        TermRelationship.objects.create(term=square,
                                        object_id=self.note.id,
                                        content_type=sherdnote_type)
        related_terms = TermRelationship.objects.get_for_object(self.note)
        self.assertEquals(len(related_terms), 1)

        post_data = {'vocabulary-%s' % str(concept.id): [str(circle.id)]}
        request = self.factory.post('/', post_data)
        update_vocabulary_terms(request, self.note)

        related_terms = TermRelationship.objects.get_for_object(self.note)
        self.assertEquals(len(related_terms), 1)
        self.assertEquals(related_terms[0].term, circle)
        self.assertEquals(related_terms[0].object_id, self.note.id)

    def test_multiple_associations_and_removals(self):
        shapes = Vocabulary.objects.get(display_name="Shapes")
        square = Term.objects.get(display_name="Square")
        circle = Term.objects.get(display_name="Circle")

        colors = Vocabulary.objects.get(display_name="Colors")
        red = Term.objects.get(display_name='Red')
        blue = Term.objects.get(display_name='Blue')

        sherdnote_type = ContentType.objects.get_for_model(self.note)

        TermRelationship.objects.create(term=square,
                                        object_id=self.note.id,
                                        content_type=sherdnote_type)
        TermRelationship.objects.create(term=red,
                                        object_id=self.note.id,
                                        content_type=sherdnote_type)
        related_terms = TermRelationship.objects.get_for_object(self.note)
        self.assertEquals(len(related_terms), 2)
        self.assertEquals(related_terms[0].term, red)
        self.assertEquals(related_terms[0].object_id, self.note.id)
        self.assertEquals(related_terms[1].term, square)
        self.assertEquals(related_terms[1].object_id, self.note.id)

        post_data = {
            'vocabulary-%s' % str(shapes.id): [str(circle.id)],
            'vocabulary-%s' % str(colors.id): [str(blue.id)],
        }
        request = self.factory.post('/', post_data)
        update_vocabulary_terms(request, self.note)

        related_terms = TermRelationship.objects.get_for_object(self.note)
        self.assertEquals(len(related_terms), 2)
        self.assertEquals(related_terms[0].term, blue)
        self.assertEquals(related_terms[0].object_id, self.note.id)
        self.assertEquals(related_terms[1].term, circle)
        self.assertEquals(related_terms[1].object_id, self.note.id)
