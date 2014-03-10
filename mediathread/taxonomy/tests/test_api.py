#pylint: disable-msg=R0904
#pylint: disable-msg=E1103
from courseaffils.models import Course
from django.contrib.contenttypes.models import ContentType
from django.http.request import HttpRequest
from mediathread.djangosherd.models import SherdNote
from mediathread.taxonomy.api import VocabularyResource, \
    TermRelationshipResource
from mediathread.taxonomy.models import Vocabulary, Term, TermRelationship
from tastypie.test import ResourceTestCase


class TaxonomyResourceTest(ResourceTestCase):
    fixtures = ['unittest_sample_course.json']

    def get_credentials(self):
        return None

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
        super(TaxonomyResourceTest, self).setUp()

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

    def test_vocabulary_get_list(self):
        self.assertTrue(
            self.api_client.client.login(username="test_student_one",
                                         password="test"))

        response = self.api_client.get('/_main/api/v1/vocabulary/',
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
            '/_main/api/v1/vocabulary/%s/' % shapes.id,
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

    def test_filter_terms_no_vocabulary(self):
        course = Course.objects.get(title="Sample Course")
        request = HttpRequest()
        request.course = course

        try:
            TermRelationshipResource().filter(request, {})
            self.assertFalse(True)
        except KeyError:
            pass  # function requires a "vocabulary" item in fitlers

    def test_filter_terms_by_vocabulary(self):
        course = Course.objects.get(title="Sample Course")
        request = HttpRequest()
        request.course = course

        vocabulary = Vocabulary.objects.get(name="shapes")
        filters = {'vocabulary': vocabulary.id}

        lst = TermRelationshipResource().filter(request, filters)
        self.assertEquals(len(lst), 1)
        self.assertEquals(lst[0]['count'], 2)
        self.assertTrue(lst[0]['last'])
        self.assertEquals(lst[0]['term__display_name'], "Square")

    def test_filter_terms_by_vocabulary_and_asset(self):
        course = Course.objects.get(title="Sample Course")
        request = HttpRequest()
        request.course = course

        vocabulary = Vocabulary.objects.get(name="shapes")
        note = SherdNote.objects.get(title="Nice Tie")
        filters = {
            'vocabulary': vocabulary.id,
            'assets': [note.asset.id]}

        lst = TermRelationshipResource().filter(request, filters)
        self.assertEquals(len(lst), 1)
        self.assertEquals(lst[0]['count'], 1)
        self.assertTrue(lst[0]['last'])
        self.assertEquals(lst[0]['term__display_name'], "Square")

    def test_filter_terms_for_alternate_course(self):
        course = Course.objects.get(title="Alternate Course")
        request = HttpRequest()
        request.course = course

        vocabulary = Vocabulary.objects.get(name="shapes")
        note = SherdNote.objects.get(title="Nice Tie")
        filters = {
            'vocabulary': vocabulary.id,
            'assets': [note.asset.id]}

        lst = TermRelationshipResource().filter(request, filters)
        self.assertEquals(len(lst), 0)

        vocabulary = Vocabulary.objects.get(name="materials")
        filters = {'vocabulary': vocabulary.id}

        lst = TermRelationshipResource().filter(request, filters)
        self.assertEquals(len(lst), 1)
        self.assertEquals(lst[0]['count'], 1)
        self.assertTrue(lst[0]['last'])
        self.assertEquals(lst[0]['term__display_name'], "Paper")
