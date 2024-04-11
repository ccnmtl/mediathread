from json import loads

from django.http.response import Http404
from django.test.client import RequestFactory
from django.test.testcases import TestCase

from mediathread.djangosherd.models import SherdNote
from mediathread.djangosherd.views import delete_annotation, edit_annotation, \
    create_annotation
from mediathread.factories import MediathreadTestMixin, AssetFactory, \
    SherdNoteFactory, ProjectFactory
from mediathread.projects.models import ProjectNote


class SherdNoteViewTest(MediathreadTestMixin, TestCase):

    def setUp(self):
        self.setup_sample_course()
        self.asset = AssetFactory(course=self.sample_course)
        self.data = {'annotation-title': 'Annotation Test',
                     'annotation-body': 'notes go here',
                     'annotation-annotation_data': '',
                     'annotation-context_pk': self.asset.id,
                     'annotation-range1': -4.5, 'annotation-range2': 23,
                     'annotation-tags': 'foo,bar', 'next': 'foo'}

    def test_create_annotation(self):
        request = RequestFactory().post('/', self.data)
        request.user = self.student_one
        response = create_annotation(request)
        self.assertEqual(response.status_code, 302)

        note = SherdNote.objects.get(title='Annotation Test')
        self.assertEqual(note.range1, -4.5)
        self.assertEqual(note.range2, 23)
        self.assertEqual(note.tags, 'foo,bar')

    def test_create_annotation_with_project(self):
        project = ProjectFactory()
        self.data['project'] = project.id

        request = RequestFactory().post('/', self.data)
        request.user = self.student_one
        response = create_annotation(request)
        self.assertEqual(response.status_code, 302)

        note = SherdNote.objects.get(title='Annotation Test')
        ProjectNote.objects.get(annotation=note, project=project)

    def test_create_annotation_ajax(self):
        request = RequestFactory().post('/', self.data,
                                        HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        request.user = self.student_one
        response = create_annotation(request)
        self.assertEqual(response.status_code, 200)

        note = SherdNote.objects.get(title='Annotation Test')

        the_json = loads(response.content)
        self.assertEqual(the_json['asset']['id'], self.asset.id)
        self.assertEqual(the_json['annotation']['id'], note.id)

    def test_delete_annotation(self):
        note = SherdNoteFactory(
            asset=self.asset, author=self.student_one,
            title='Selection', range1=116.25, range2=6.75)

        request = RequestFactory().post('/', {'next': 'foo'})
        request.user = self.student_two
        response = delete_annotation(request, note.id)
        self.assertEqual(response.status_code, 403)

        request.user = self.student_one
        response = delete_annotation(request, note.id)
        self.assertEqual(response.status_code, 302)

        with self.assertRaises(SherdNote.DoesNotExist):
            SherdNote.objects.get(title='Selection')

    def test_edit_annotation(self):
        note = SherdNoteFactory(
            asset=self.asset, author=self.student_one,
            title='Selection', range1=116.25, range2=6.75)

        data = {'annotation-range1': -4.5,
                'annotation-tags': 'foo,bar', 'next': 'foo'}
        request = RequestFactory().post('/', data)
        request.user = self.student_two

        with self.assertRaises(Http404):
            edit_annotation(request, 123)

        response = edit_annotation(request, note.id)
        self.assertEqual(response.status_code, 403)

        # via post
        request.user = self.student_one
        response = edit_annotation(request, note.id)
        self.assertEqual(response.status_code, 302)
        note.refresh_from_db()
        self.assertEqual(note.range1, -4.5)
        self.assertEqual(note.tags, 'foo,bar')

        # via ajax
        data = {'annotation-range2': 7}
        request = RequestFactory().post('/', data,
                                        HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        request.user = self.student_one
        response = edit_annotation(request, note.id)
        self.assertEqual(response.status_code, 200)
        the_json = loads(response.content)
        self.assertEqual(the_json['asset']['id'], self.asset.id)
        self.assertEqual(the_json['annotation']['id'], note.id)
        note.refresh_from_db()
        self.assertEqual(note.range2, 7)
