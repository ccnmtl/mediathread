# pylint: disable-msg=R0904
import json

from django.test import TestCase

from mediathread.factories import MediathreadTestMixin, UserFactory, \
    AssetFactory, SherdNoteFactory, ProjectFactory
from mediathread.projects.models import Project


class ProjectViewTest(MediathreadTestMixin, TestCase):
    def setUp(self):
        self.setup_sample_course()
        self.setup_alternate_course()

        # instructor that sees both Sample Course & Alternate Course
        self.instructor_three = UserFactory(username='instructor_three')
        self.add_as_faculty(self.sample_course, self.instructor_three)
        self.add_as_faculty(self.alt_course, self.instructor_three)

        # Sample Course Image Asset
        self.asset1 = AssetFactory.create(course=self.sample_course,
                                          primary_source='image')

        self.student_note = SherdNoteFactory(
            asset=self.asset1, author=self.student_one,
            tags=',student_one_selection',
            body='student one selection note', range1=0, range2=1)
        self.student_ga = SherdNoteFactory(
            asset=self.asset1, author=self.student_one,
            tags=',student_one_item',
            body='student one item note',
            title=None, range1=None, range2=None)
        self.instructor_note = SherdNoteFactory(
            asset=self.asset1, author=self.instructor_one,
            tags=',image, instructor_one_selection,',
            body='instructor one selection note', range1=0, range2=1)
        self.instructor_ga = SherdNoteFactory(
            asset=self.asset1, author=self.instructor_one,
            tags=',image, instructor_one_item,',
            body='instructor one item note',
            title=None, range1=None, range2=None)

        # Sample Course Projects
        self.project_private = ProjectFactory.create(
            course=self.sample_course, author=self.student_one,
            policy='PrivateEditorsAreOwners')
        self.add_citation(self.project_private, self.student_note)
        self.add_citation(self.project_private, self.student_ga)

        self.project_instructor_shared = ProjectFactory.create(
            course=self.sample_course, author=self.student_one,
            policy='InstructorShared')
        self.add_citation(self.project_instructor_shared, self.student_note)
        self.add_citation(self.project_instructor_shared, self.student_ga)

        self.project_class_shared = ProjectFactory.create(
            course=self.sample_course, author=self.student_one,
            policy='CourseProtected')
        self.add_citation(self.project_class_shared, self.student_note)
        self.add_citation(self.project_class_shared, self.student_ga)

        self.assignment = ProjectFactory.create(
            course=self.sample_course, author=self.instructor_one,
            policy='Assignment')

        # Alt Course Projects
        self.project_private_alt_course = ProjectFactory.create(
            course=self.alt_course, author=self.alt_student,
            policy='PrivateEditorsAreOwners')

        self.project_public_alt_course = ProjectFactory.create(
            course=self.alt_course, author=self.alt_student,
            policy='PrivateEditorsAreOwners')

    def test_project_save_doesnotexist(self):
        self.assertTrue(
            self.client.login(username=self.student_one.username,
                              password='test'))

        # Does not exist
        response = self.client.post('/project/save/1001/', {},
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEquals(response.status_code, 404)

    def test_project_save_cannot_edit(self):
        self.assertTrue(
            self.client.login(username=self.instructor_one.username,
                              password='test'))

        # Forbidden to save or view
        url = '/project/save/%s/' % self.project_private.id
        response = self.client.post(url, follow=True,
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEquals(response.status_code, 403)
        self.assertEquals(len(response.redirect_chain), 1)
        elt = response.redirect_chain[0]

        view = 'project/view/%s/' % self.project_private.id
        self.assertTrue(elt[0].endswith(view))
        self.assertEquals(elt[1], 302)

    def test_project_save_nonajax(self):
        self.assertTrue(
            self.client.login(username=self.student_one.username,
                              password='test'))

        url = '/project/save/%s/' % self.project_private.id
        response = self.client.post(url)
        self.assertEquals(response.status_code, 405)

    def test_project_save_valid(self):
        self.assertTrue(self.client.login(username=self.student_one.username,
                                          password='test'))

        data = {u'body': [u'<p>abcdefghi</p>'],
                u'participants': [self.student_one.id],
                u'publish': [u'PrivateEditorsAreOwners'],
                u'title': [u'Private Student Essay']}

        url = '/project/save/%s/' % self.project_private.id
        response = self.client.post(url, data,
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEquals(response.status_code, 200)

        the_json = json.loads(response.content)
        self.assertEquals(the_json["status"], "success")
        self.assertFalse(the_json["is_assignment"])
        self.assertEquals(the_json["title"], "Private Student Essay")
        self.assertEquals(the_json["revision"]["visibility"], "Private")
        self.assertIsNone(the_json["revision"]["public_url"])
        self.assertEquals(the_json["revision"]["due_date"], "")

    def test_project_save_invalid_title(self):
        self.assertTrue(self.client.login(username=self.student_one.username,
                                          password='test'))

        data = {u'body': [u'<p>abcdefghi</p>'],
                u'participants': [self.student_one.id],
                u'publish': [u'PrivateEditorsAreOwners'],
                u'title': [u'']}

        url = '/project/save/%s/' % self.project_private.id
        response = self.client.post(url, data,
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEquals(response.status_code, 200)

        the_json = json.loads(response.content)
        self.assertEquals(the_json["status"], "error")
        self.assertTrue(the_json["msg"].startswith(' "" is not valid'))

    def test_project_create_and_save(self):
        self.assertTrue(self.client.login(username=self.student_one.username,
                                          password='test'))

        data = {u'participants': [self.student_one.id],
                u'publish': [u'PrivateEditorsAreOwners']}

        response = self.client.post('/project/create/', data, follow=True)
        self.assertEquals(response.status_code, 200)
        self.assertTrue(response.redirect_chain[0][0].startswith(
            'http://testserver/project/view/'))

        project = Project.objects.get(course=self.sample_course,
                                      title='Untitled')
        self.assertEquals(project.versions.count(), 1)
        self.assertIsNone(project.submitted_date())

        data = {u'body': [u'<p>abcdefghi</p>'],
                u'participants': [self.student_one.id],
                u'publish': [u'InstructorShared'],
                u'title': [u'Student Essay']}

        url = '/project/save/%s/' % project.id
        response = self.client.post(url, data,
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEquals(response.status_code, 200)

        project = Project.objects.get(title='Student Essay')
        self.assertEquals(project.versions.count(), 2)
        self.assertIsNotNone(project.submitted_date())
