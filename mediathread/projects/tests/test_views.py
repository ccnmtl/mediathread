#pylint: disable-msg=R0904
from django.contrib.auth.models import User
from django.test import TestCase
from mediathread.projects.models import Project
import simplejson


class ProjectViewTest(TestCase):
    fixtures = ['unittest_sample_course.json',
                'unittest_sample_projects.json']

    def test_project_save_doesnotexist(self):
        self.assertTrue(
            self.client.login(username='test_student_one', password='test'))

        # Does not exist
        response = self.client.post('/project/save/100/',
                                    {},
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEquals(response.status_code, 404)

    def test_project_save_cannot_edit(self):
        self.assertTrue(
            self.client.login(username='test_instructor', password='test'))

        # Forbidden to save or view
        response = self.client.post('/project/save/1/',
                                    follow=True,
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEquals(response.status_code, 403)
        self.assertEquals(len(response.redirect_chain), 1)
        elt = response.redirect_chain[0]
        self.assertTrue(elt[0].endswith('project/view/1/'))
        self.assertEquals(elt[1], 302)

    def test_project_save_nonajax(self):
        self.assertTrue(
            self.client.login(username='test_student_one', password='test'))

        response = self.client.post('/project/save/1/')
        self.assertEquals(response.status_code, 404)

    def test_project_save_valid(self):
        user = User.objects.get(username="test_student_one")

        project = Project.objects.get(id=1)
        self.assertTrue(project.author.username, "test_student_one")
        self.assertEquals(project.title, "Private Composition")

        self.assertTrue(self.client.login(username='test_student_one',
                                          password='test'))

        data = {u'body': [u'<p>abcdefghi</p>'],
                u'participants': [user.id],
                u'publish': [u'PrivateEditorsAreOwners'],
                u'title': [u'Private Student Essay']}

        response = self.client.post('/project/save/1/',
                                    data,
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEquals(response.status_code, 200)

        json = simplejson.loads(response.content)
        self.assertEquals(json["status"], "success")
        self.assertFalse(json["is_assignment"])
        self.assertEquals(json["title"], "Private Student Essay")
        self.assertEquals(json["revision"]["id"], 2)
        self.assertEquals(json["revision"]["visibility"], "Private")
        self.assertIsNone(json["revision"]["public_url"])
        self.assertEquals(json["revision"]["due_date"], "")

    def test_project_save_invalid_title(self):
        user = User.objects.get(username="test_student_one")

        project = Project.objects.get(id=1)
        self.assertTrue(project.author.username, "test_student_one")
        self.assertEquals(project.title, "Private Composition")

        self.assertTrue(self.client.login(username='test_student_one',
                                          password='test'))

        data = {u'body': [u'<p>abcdefghi</p>'],
                u'participants': [user.id],
                u'publish': [u'PrivateEditorsAreOwners'],
                u'title': [u'']}

        response = self.client.post('/project/save/1/',
                                    data,
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEquals(response.status_code, 200)

        json = simplejson.loads(response.content)
        self.assertEquals(json["status"], "error")
        self.assertTrue(json["msg"].startswith(' "" is not valid'))
