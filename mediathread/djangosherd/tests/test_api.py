from datetime import datetime

from django.test.client import RequestFactory
from django.test.testcases import TestCase

from mediathread.djangosherd.api import DiscussionIndexResource, \
    SherdNoteResource
from mediathread.djangosherd.models import DiscussionIndex
from mediathread.factories import MediathreadTestMixin, AssetFactory, \
    SherdNoteFactory, ProjectNoteFactory
from mediathread.projects.tests.factories import ProjectSequenceAssetFactory
from mediathread.sequence.tests.factories import SequenceAssetFactory, \
    SequenceMediaElementFactory
from mediathread.taxonomy.models import Term


class DiscussionIndexResourcesTest(MediathreadTestMixin, TestCase):

    def test_render(self):
        self.setup_sample_course()
        self.create_discussion(self.sample_course, self.instructor_one)

        indicies = DiscussionIndex.objects.all()

        request = RequestFactory().get('/')
        request.course = self.sample_course
        request.user = self.instructor_one
        ctx = DiscussionIndexResource().render_list(request, indicies)
        self.assertTrue('references' in ctx)
        self.assertEquals(ctx['references'][0]['title'],
                          'Sample Course Discussion')
        self.assertEquals(ctx['references'][0]['type'], 'discussion')


class SherdNoteResourceTest(MediathreadTestMixin, TestCase):

    def setUp(self):
        self.setup_sample_course()
        asset = AssetFactory(author=self.student_one, primary_source='image',
                             course=self.sample_course)

        self.note1 = SherdNoteFactory(
            asset=asset, author=self.student_one,
            title='one', range1=116.25, range2=6.75)

        self.note2 = SherdNoteFactory(
            asset=asset, author=self.student_one,
            title='two', range1=116.25, range2=6.75)

    def test_in_selection_assignment_response(self):
        res = SherdNoteResource()
        self.assertFalse(res.in_selection_assignment_response(self.note1))

        pn = ProjectNoteFactory(annotation=self.note1)
        pn.project.date_submitted = datetime.today()
        pn.project.save()
        self.assertTrue(res.in_selection_assignment_response(self.note1))

        request = RequestFactory().get('/?citable=true')
        request.user = self.student_one
        request.course = self.sample_course
        bundle = SherdNoteResource().build_bundle(
            obj=self.note1, request=request)
        res.dehydrate(bundle)
        self.assertEquals(bundle.data['editable'], False)
        self.assertEquals(bundle.data['citable'], True)

    def test_in_sequence_assignment_response(self):
        res = SherdNoteResource()
        self.assertFalse(res.in_sequence_assignment_response(self.note1))
        self.assertFalse(res.in_sequence_assignment_response(self.note2))

        sa = SequenceAssetFactory(spine=self.note1)
        psa = ProjectSequenceAssetFactory(sequence_asset=sa)
        self.assertFalse(res.in_sequence_assignment_response(self.note1))

        psa.project.date_submitted = datetime.today()
        psa.project.save()
        self.assertTrue(res.in_sequence_assignment_response(self.note1))

        SequenceMediaElementFactory(sequence_asset=sa, media=self.note2)
        self.assertTrue(res.in_sequence_assignment_response(self.note2))

        request = RequestFactory().get('/?citable=true')
        request.user = self.student_one
        request.course = self.sample_course
        bundle = SherdNoteResource().build_bundle(
            obj=self.note1, request=request)
        res.dehydrate(bundle)
        self.assertEquals(bundle.data['editable'], False)
        self.assertEquals(bundle.data['citable'], True)

    def test_render_related_terms(self):
        taxonomy = {
            'Shapes': ['Square', 'Triangle'],
            'Colors': ['Red', 'Blue', 'Green']
        }
        self.create_vocabularies(self.sample_course, taxonomy)

        term = Term.objects.get(name='square')
        self.create_term_relationship(self.note1, term)
        term = Term.objects.get(name='triangle')
        self.create_term_relationship(self.note1, term)
        term = Term.objects.get(name='red')
        self.create_term_relationship(self.note1, term)

        res = SherdNoteResource()
        request = RequestFactory().get('')
        bundle = SherdNoteResource().build_bundle(
            obj=self.note1, request=request)

        values = res.render_related_terms(bundle)
        self.assertEquals(len(values), 2)
        self.assertEquals(values[0]['terms'][0]['display_name'], 'Square')
        self.assertEquals(values[0]['terms'][1]['display_name'], 'Triangle')
        self.assertEquals(values[1]['terms'][0]['display_name'], 'Red')

    def test_dehydrate(self):
        res = SherdNoteResource()
        request = RequestFactory().get('/?citable=true')
        request.user = self.student_one
        bundle = SherdNoteResource().build_bundle(
            obj=self.note1, request=request)

        res.dehydrate(bundle)
        self.assertEquals(bundle.data['vocabulary'], [])
        self.assertEquals(bundle.data['is_null'], False)
        self.assertEquals(bundle.data['editable'], True)
        self.assertEquals(bundle.data['is_global_annotation'], False)
        self.assertEquals(bundle.data['citable'], True)
