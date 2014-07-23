#pylint: disable-msg=R0904
#pylint: disable-msg=E1103
from courseaffils.models import Course
from django.test import TestCase
from django.test.client import Client
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


class MigrateMaterialsTest(TestCase):
    # Use ``fixtures`` & ``urls`` as normal. See Django's ``TestCase``
    # documentation for the gory details.
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
