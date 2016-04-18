# pylint: disable-msg=R0904
from django.test.client import RequestFactory
from django.test.testcases import TestCase

from mediathread.factories import AssetFactory, SherdNoteFactory, \
    MediathreadTestMixin
from mediathread.taxonomy.models import Term, TermRelationship
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
        term = Term.objects.get(display_name="Square")
        self.assertEquals(term.termrelationship_set.count(), 0)

        post_data = {'vocabulary': [str(term.id)]}
        request = self.factory.post('/', post_data)
        update_vocabulary_terms(request, self.note)

        related = term.termrelationship_set.first()
        self.assertIsNotNone(related)
        self.assertEquals(related.term, term)
        self.assertEquals(related.sherdnote, self.note)

    def test_removal(self):
        term = Term.objects.get(display_name="Square")

        TermRelationship.objects.create(term=term, sherdnote=self.note)
        self.assertEquals(term.termrelationship_set.count(), 1)

        request = self.factory.post('/', {})
        update_vocabulary_terms(request, self.note)

        self.assertEquals(term.termrelationship_set.count(), 0)

    def test_removal_and_association(self):
        square = Term.objects.get(display_name="Square")
        circle = Term.objects.get(display_name="Circle")

        TermRelationship.objects.create(term=square, sherdnote=self.note)
        self.assertEquals(square.termrelationship_set.count(), 1)

        post_data = {'vocabulary': [str(circle.id)]}
        request = self.factory.post('/', post_data)
        update_vocabulary_terms(request, self.note)

        related = circle.termrelationship_set.first()
        self.assertEquals(related.term, circle)
        self.assertEquals(related.sherdnote, self.note)

    def test_multiple_associations_and_removals(self):
        square = Term.objects.get(display_name="Square")
        circle = Term.objects.get(display_name="Circle")

        red = Term.objects.get(display_name='Red')
        blue = Term.objects.get(display_name='Blue')

        TermRelationship.objects.create(term=square, sherdnote=self.note)
        TermRelationship.objects.create(term=red, sherdnote=self.note)
        related_terms = TermRelationship.objects.filter(sherdnote=self.note)
        self.assertEquals(len(related_terms), 2)
        self.assertEquals(related_terms[0].term, red)
        self.assertEquals(related_terms[0].sherdnote, self.note)
        self.assertEquals(related_terms[1].term, square)
        self.assertEquals(related_terms[1].sherdnote, self.note)

        post_data = {
            'vocabulary': [str(circle.id), str(blue.id)]
        }
        request = self.factory.post('/', post_data)
        update_vocabulary_terms(request, self.note)

        related_terms = TermRelationship.objects.filter(sherdnote=self.note)
        self.assertEquals(len(related_terms), 2)
        self.assertEquals(related_terms[0].term, blue)
        self.assertEquals(related_terms[0].sherdnote, self.note)
        self.assertEquals(related_terms[1].term, circle)
        self.assertEquals(related_terms[1].sherdnote, self.note)
