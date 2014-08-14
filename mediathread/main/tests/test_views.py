#pylint: disable-msg=R0904
#pylint: disable-msg=E1103
from courseaffils.models import Course
from django.contrib.auth.models import User
from django.http.response import Http404
from django.test import TestCase
from django.test.client import Client, RequestFactory
from mediathread.assetmgr.models import Asset
from mediathread.main.views import MigrateCourseView
from mediathread.projects.models import Project
import json


class SimpleViewTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_index(self):
        # it should redirect us somewhere.
        response = self.client.get("/")
        self.assertEquals(response.status_code, 302)
        # for now, we don't care where. really, we
        # are just making sure it's not a 500 error
        # at this point

    def test_smoke(self):
        # run the smoketests. we don't care if they pass
        # or fail, we just want to make sure that the
        # smoketests themselves don't have an error
        response = self.client.get("/smoketest/")
        self.assertEquals(response.status_code, 200)


class MigrateCourseViewTest(TestCase):
    fixtures = ['unittest_sample_course.json',
                'unittest_sample_projects.json']

    def setUp(self):
        self.factory = RequestFactory()
        self.faculty = User.objects.get(username='test_instructor_two')

        self.superuser = User.objects.create(username='ccnmtl',
                                             password='test',
                                             is_superuser=True,
                                             is_staff=True)

        self.sample_course = Course.objects.get(title='Sample Course')
        self.alt_course = Course.objects.get(title="Alternate Course")

    def test_as_student(self):
        self.assertTrue(
            self.client.login(username='test_student_one', password='test'))
        response = self.client.get('/dashboard/migrate/')
        self.assertEquals(response.status_code, 403)

    def test_not_logged_in(self):
        response = self.client.get('/dashboard/migrate/')
        self.assertEquals(response.status_code, 302)

    def test_get_context_data(self):
        request = RequestFactory().get('/dashboard/migrate/')
        request.user = User.objects.get(username='test_instructor_two')
        request.course = self.sample_course

        view = MigrateCourseView()
        view.request = request

        ctx = view.get_context_data()

        self.assertEquals(len(ctx['current_course_faculty']), 2)
        self.assertEquals(ctx['current_course_faculty'][0].username,
                          'test_instructor')
        self.assertEquals(ctx['current_course_faculty'][1].username,
                          'test_instructor_two')

        self.assertEquals(len(ctx['available_courses']), 2)
        self.assertEquals(ctx['available_courses'][0].title,
                          'Alternate Course')
        self.assertEquals(ctx['available_courses'][1].title,
                          'Sample Course')

        request.user = self.superuser
        ctx = view.get_context_data()
        self.assertEquals(len(ctx['available_courses']), 2)
        self.assertEquals(ctx['available_courses'][0].title,
                          'Alternate Course')
        self.assertEquals(ctx['available_courses'][1].title,
                          'Sample Course')

    def test_post_invalidcourse(self):
        data = {
            'fromCourse': 23
        }

        request = RequestFactory().post('/dashboard/migrate/', data)
        request.user = self.superuser
        request.course = self.sample_course

        view = MigrateCourseView()
        view.request = request

        self.assertRaises(Http404, view.post, request)

    def test_post_on_behalf_of_student(self):
        student = User.objects.get(username='test_student_alt')
        data = {
            'fromCourse': self.alt_course.id,
            'on_behalf_of': student.id
        }

        request = RequestFactory().post('/dashboard/migrate/', data)
        request.user = self.superuser
        request.course = self.sample_course

        view = MigrateCourseView()
        view.request = request
        response = view.post(request)

        the_json = json.loads(response.content)
        self.assertFalse(the_json['success'])

    def test_post_on_behalf_of_faculty(self):
        teacher = User.objects.get(username='test_instructor_alt')
        data = {
            'fromCourse': self.alt_course.id,
            'on_behalf_of': teacher.id
        }

        request = RequestFactory().post('/dashboard/migrate/', data)
        request.user = self.superuser
        request.course = self.sample_course

        view = MigrateCourseView()
        view.request = request
        response = view.post(request)

        the_json = json.loads(response.content)
        self.assertFalse(the_json['success'])

    def test_post(self):
        asset1 = Asset.objects.get(
            course=self.sample_course,
            title="The Armory - Home to CCNMTL'S CUMC Office")
        project1 = Project.objects.get(
            course=self.sample_course, title='Sample Course Assignment')
        data = {
            'fromCourse': self.sample_course.id,
            'asset_ids[]': [asset1.id],
            'project_ids[]': [project1.id]
        }

        # Migrate assets from SampleCourse into Alternate Course
        # test_instructor_two is a member of both courses
        request = RequestFactory().post('/dashboard/migrate/', data)
        request.user = User.objects.get(username='test_instructor_two')
        request.course = self.alt_course

        view = MigrateCourseView()
        view.request = request
        response = view.post(request)

        the_json = json.loads(response.content)
        self.assertTrue(the_json['success'])
        self.assertEquals(the_json['asset_count'], 4)
        self.assertEquals(the_json['project_count'], 1)
        self.assertEquals(the_json['note_count'], 6)

        Asset.objects.get(
            course=self.alt_course,
            title="The Armory - Home to CCNMTL'S CUMC Office")
        Asset.objects.get(
            course=self.alt_course,
            title="Mediathread: Introduction")
        Asset.objects.get(course=self.alt_course, title="MAAP Award Reception")
        Asset.objects.get(course=self.alt_course, title="Project Portfolio")

        project1 = Project.objects.get(
            course=self.alt_course, title='Sample Course Assignment')
        self.assertEquals(len(project1.citations()), 5)


class MigrateMaterialsTest(TestCase):
    fixtures = ['unittest_sample_course.json',
                'unittest_sample_projects.json']

    def get_credentials(self):
        return None

    def test_as_student(self):
        self.assertTrue(self.client.login(username="test_student_one",
                                          password="test"))

        sample_course = Course.objects.get(title="Sample Course")

        response = self.client.get('/dashboard/migrate/materials/%s/' %
                                   sample_course.id, {},
                                   HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEquals(response.status_code, 403)

    def test_sample_course(self):
        self.assertTrue(self.client.login(username="test_instructor",
                                          password="test"))

        sample_course = Course.objects.get(title="Sample Course")

        url = '/dashboard/migrate/materials/%s/' % sample_course.id

        response = self.client.get(url, {},
                                   HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEquals(response.status_code, 200)

        the_json = json.loads(response.content)
        self.assertEquals(the_json['course']['title'], 'Sample Course')
        self.assertEquals(len(the_json['assets']), 4)

        self.assertEquals(the_json['assets'][0]['title'],
                          'Mediathread: Introduction')
        self.assertEquals(the_json['assets'][0]['annotation_count'], 4)

        self.assertEquals(the_json['assets'][1]['title'],
                          'Project Portfolio')
        self.assertEquals(the_json['assets'][1]['annotation_count'], 0)

        self.assertEquals(the_json['assets'][2]['title'],
                          'MAAP Award Reception')
        self.assertEquals(the_json['assets'][2]['annotation_count'], 1)

        self.assertEquals(the_json['assets'][3]['title'],
                          "The Armory - Home to CCNMTL'S CUMC Office")
        self.assertEquals(the_json['assets'][3]['annotation_count'], 1)

        self.assertEquals(len(the_json['projects']), 1)

    def test_alternate_course(self):
        self.assertTrue(self.client.login(username="test_instructor_alt",
                                          password="test"))

        sample_course = Course.objects.get(title="Alternate Course")

        url = '/dashboard/migrate/materials/%s/' % sample_course.id

        response = self.client.get(url, {},
                                   HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEquals(response.status_code, 200)

        the_json = json.loads(response.content)
        self.assertEquals(the_json['course']['title'], 'Alternate Course')
        self.assertEquals(len(the_json['assets']), 1)

        self.assertEquals(the_json['assets'][0]['title'],
                          'Design Research')
        self.assertEquals(the_json['assets'][0]['annotation_count'], 2)

        self.assertEquals(len(the_json['projects']), 1)
