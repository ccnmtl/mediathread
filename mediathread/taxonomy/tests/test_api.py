#pylint: disable-msg=R0904
#pylint: disable-msg=E1103
from courseaffils.models import Course
from django.contrib.auth.models import User
from django.http.request import HttpRequest
from django.test.client import RequestFactory
from mediathread.djangosherd.models import SherdNote
from mediathread.taxonomy.api import VocabularyResource, \
    VocabularyAuthorization
from mediathread.taxonomy.models import Vocabulary
from mediathread.taxonomy.tests.factories import TaxonomyTestCase


class TaxonomyApiTest(TaxonomyTestCase):

    def get_credentials(self):
        return None

    def test_vocabulary_authorization(self):
        factory = RequestFactory()
        request = factory.get('')
        request.course = Course.objects.get(title='Sample Course')
        request.user = User.objects.get(username='test_instructor')

        vocabulary = Vocabulary.objects.all()
        authorization = VocabularyAuthorization()

        bundle = VocabularyResource().build_bundle(obj=vocabulary,
                                                   request=request)

        lst = authorization.read_list(vocabulary, bundle)
        self.assertEquals(len(lst), 2)

    def test_vocabulary_get_list(self):
        self.assertTrue(
            self.api_client.client.login(username="test_student_one",
                                         password="test"))

        response = self.api_client.get('/api/vocabulary/',
                                       format='json')
        self.assertValidJSONResponse(response)

        json = self.deserialize(response)
        lst = json['objects']
        self.assertEquals(len(lst), 2)
        self.assertEquals(lst[0]['display_name'], "Colors")
        self.assertEquals(len(lst[0]['term_set']), 3)
        self.assertEquals(lst[1]['display_name'], "Shapes")
        self.assertEquals(len(lst[1]['term_set']), 2)

    def test_vocabulary_render_list(self):
        course = Course.objects.get(title="Sample Course")
        request = HttpRequest()
        request.course = course

        lst = VocabularyResource().render_list(
            request, Vocabulary.objects.get_for_object(request.course))

        self.assertEquals(len(lst), 2)
        self.assertEquals(lst[0]['display_name'], "Colors")
        self.assertEquals(len(lst[0]['term_set']), 3)
        self.assertEquals(lst[1]['display_name'], "Shapes")
        self.assertEquals(len(lst[1]['term_set']), 2)

    def test_vocabulary_get_one(self):
        self.assertTrue(
            self.api_client.client.login(username="test_student_one",
                                         password="test"))

        shapes = Vocabulary.objects.get(name="shapes")
        response = self.api_client.get(
            '/api/vocabulary/%s/' % shapes.id,
            format='json')
        self.assertValidJSONResponse(response)

        detail = self.deserialize(response)
        self.assertEquals(detail['display_name'], "Shapes")
        self.assertEquals(len(detail['term_set']), 2)

    def test_vocabulary_render_one(self):
        course = Course.objects.get(title="Sample Course")
        request = HttpRequest()
        request.course = course

        vocabulary = Vocabulary.objects.get(name="shapes")
        detail = VocabularyResource().render_one(request, vocabulary)
        self.assertEquals(detail['display_name'], "Shapes")
        self.assertEquals(len(detail['term_set']), 2)

    def test_vocabulary_render_related(self):
        course = Course.objects.get(title="Sample Course")
        request = HttpRequest()
        request.course = course

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
        course = Course.objects.get(title="Sample Course")
        request = HttpRequest()
        request.course = course

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
