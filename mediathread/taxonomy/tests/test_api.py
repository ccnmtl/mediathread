# pylint: disable-msg=R0904
# pylint: disable-msg=E1103
import json

from django.contrib.auth.models import User
from django.http.request import HttpRequest
from django.test.client import RequestFactory
from django.test import TestCase

from mediathread.djangosherd.models import SherdNote
from mediathread.factories import MediathreadTestMixin, AssetFactory, \
    SherdNoteFactory
from mediathread.taxonomy.api import VocabularyResource, \
    VocabularyAuthorization
from mediathread.taxonomy.models import Vocabulary, Term, TermRelationship


class TaxonomyApiTest(MediathreadTestMixin, TestCase):

    def get_credentials(self):
        return None

    def setUp(self):
        self.setup_sample_course()
        self.setup_alternate_course()

        taxonomy = {
            'Shapes': ['Square', 'Triangle'],
            'Colors': ['Red', 'Blue', 'Green']
        }
        self.create_vocabularies(self.sample_course, taxonomy)

        taxonomy = {
            'Materials': ['Paper', 'Wood', 'Stone']
        }
        self.create_vocabularies(self.alt_course, taxonomy)

        asset = AssetFactory(course=self.sample_course,
                             author=self.student_one, title="Asset One")

        # instructor_one in Sample Course
        note = SherdNoteFactory(
            asset=asset, author=self.student_three,
            title="Nice Tie", tags=',student_three_selection',
            body='student three selection note', range1=0, range2=1)
        term = Term.objects.get(name="square")
        self.create_term_relationship(note, term)

        note = SherdNoteFactory(
            asset=asset, author=self.instructor_one,
            title="Left Corner", tags=',instructor_one_selection',
            body='instructor one selection note', range1=0, range2=1)
        term = Term.objects.get(name="square")
        self.create_term_relationship(note, term)
        term = Term.objects.get(name="red")
        self.create_term_relationship(note, term)

        # alt_student in Alternate Course
        asset = AssetFactory(course=self.alt_course,
                             author=self.alt_student, title="Asset Two")
        note = SherdNoteFactory(
            asset=asset, author=self.student_two,
            title="Whole Item Selection", tags=',alt_student_selection',
            body='alt student selection note', range1=0, range2=1)
        term = Term.objects.get(name="paper")
        self.create_term_relationship(note, term)

    def test_single_term_relationship(self):
        notes = SherdNote.objects.filter(asset__title='Asset Two')

        lst = TermRelationship.objects.get_for_object_list(notes)
        self.assertEquals(len(lst), 1)
        self.assertEquals(lst[0].term, Term.objects.get(name='paper'))

    def test_multiple_term_relationship(self):
        notes = SherdNote.objects.filter(asset__title="Asset One")

        lst = TermRelationship.objects.get_for_object_list(notes)

        self.assertEquals(len(lst), 3)
        self.assertEquals(lst[0].term, Term.objects.get(name='red'))
        self.assertEquals(lst[1].term, Term.objects.get(name='square'))
        self.assertEquals(lst[2].term, Term.objects.get(name='square'))

    def test_vocabulary_authorization(self):
        factory = RequestFactory()
        request = factory.get('')
        request.course = self.sample_course
        request.user = User.objects.get(username='instructor_one')

        vocabulary = Vocabulary.objects.all()
        authorization = VocabularyAuthorization()

        bundle = VocabularyResource().build_bundle(obj=vocabulary,
                                                   request=request)

        lst = authorization.read_list(vocabulary, bundle)
        self.assertEquals(len(lst), 2)

    def test_vocabulary_get_list(self):
        self.assertTrue(self.client.login(username=self.student_one.username,
                                          password="test"))

        response = self.client.get('/api/vocabulary/',
                                   {},
                                   HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        the_json = json.loads(response.content)
        lst = the_json['objects']
        self.assertEquals(len(lst), 2)
        self.assertEquals(lst[0]['display_name'], "Colors")
        self.assertEquals(len(lst[0]['term_set']), 3)
        self.assertEquals(lst[1]['display_name'], "Shapes")
        self.assertEquals(len(lst[1]['term_set']), 2)

    def test_vocabulary_render_list(self):
        request = HttpRequest()
        request.course = self.sample_course

        lst = VocabularyResource().render_list(
            request, Vocabulary.objects.get_for_object(request.course))

        self.assertEquals(len(lst), 2)
        self.assertEquals(lst[0]['display_name'], "Colors")
        self.assertEquals(len(lst[0]['term_set']), 3)
        self.assertEquals(lst[1]['display_name'], "Shapes")
        self.assertEquals(len(lst[1]['term_set']), 2)

    def test_vocabulary_get_one(self):
        self.assertTrue(
            self.client.login(username="student_one", password="test"))

        shapes = Vocabulary.objects.get(name="shapes")
        response = self.client.get('/api/vocabulary/%s/' % shapes.id,
                                   {},
                                   HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        the_json = json.loads(response.content)
        self.assertEquals(the_json['display_name'], "Shapes")
        self.assertEquals(len(the_json['term_set']), 2)

    def test_vocabulary_render_one(self):
        request = HttpRequest()
        request.course = self.sample_course

        vocabulary = Vocabulary.objects.get(name="shapes")
        detail = VocabularyResource().render_one(request, vocabulary)
        self.assertEquals(detail['display_name'], "Shapes")
        self.assertEquals(len(detail['term_set']), 2)

    def test_vocabulary_render_related(self):
        request = HttpRequest()
        request.course = self.sample_course

        notes = SherdNote.objects.filter(title='Left Corner')
        ctx = VocabularyResource().render_related(request, notes)

        self.assertEquals(len(ctx), 2)
        self.assertEquals(ctx[0]['display_name'], 'Colors')
        self.assertEquals(len(ctx[0]['term_set']), 1)
        self.assertEquals(ctx[0]['term_set'][0]['display_name'], 'Red')
        self.assertEquals(ctx[0]['term_set'][0]['count'], 1)

        self.assertEquals(ctx[1]['display_name'], 'Shapes')
        self.assertEquals(len(ctx[1]['term_set']), 1)
        self.assertEquals(ctx[1]['term_set'][0]['display_name'], 'Square')
        self.assertEquals(ctx[1]['term_set'][0]['count'], 1)

    def test_vocabulary_render_related_multiple(self):
        request = HttpRequest()
        request.course = self.sample_course

        notes = SherdNote.objects.filter(title__in=['Left Corner', 'Nice Tie'])
        ctx = VocabularyResource().render_related(request, notes)

        self.assertEquals(len(ctx), 2)
        self.assertEquals(ctx[0]['display_name'], 'Colors')
        self.assertEquals(len(ctx[0]['term_set']), 1)
        self.assertEquals(ctx[0]['term_set'][0]['display_name'], 'Red')
        self.assertEquals(ctx[0]['term_set'][0]['count'], 1)

        self.assertEquals(ctx[1]['display_name'], 'Shapes')
        self.assertEquals(len(ctx[1]['term_set']), 1)
        self.assertEquals(ctx[1]['term_set'][0]['display_name'], 'Square')
        self.assertEquals(ctx[1]['term_set'][0]['count'], 2)
