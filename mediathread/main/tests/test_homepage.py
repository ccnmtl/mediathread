#pylint: disable-msg=R0904
#pylint: disable-msg=E1103
from django.test import TestCase
from django.test.client import Client
import simplejson


class HomepageTest(TestCase):
    fixtures = ['unittest_sample_course.json',
                'unittest_sample_projects.json']

    def assertProjectEquals(self, project, title, author, editable):
        self.assertEquals(project['title'], title)
        self.assertEquals(project['authors'][0]['name'], author)
        self.assertEquals(project['editable'], editable)

    def test_get_my_projectlist_as_student(self):
        client = Client()

        self.assertTrue(
            client.login(username='test_student_one', password='test'))

        response = client.get('/yourspace/projects/test_student_one/',
                              {},
                              HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        json = simplejson.loads(response.content)

        assignments = json['assignments']
        self.assertEquals(len(assignments), 1)
        self.assertEquals(assignments[0]['title'], "Sample Course Assignment")
        self.assertTrue(assignments[0]['display_as_assignment'])
        self.assertFalse(assignments[0]['is_faculty'])

        projects = json['projects']
        self.assertEquals(len(projects), 3)

        self.assertProjectEquals(projects[0],
                                 'Public To Class Composition',
                                 'Student One',
                                 True)

        self.assertProjectEquals(projects[1],
                                 'Instructor Shared',
                                 'Student One',
                                 True)

        self.assertProjectEquals(projects[2],
                                 'Private Composition',
                                 'Student One',
                                 True)

    def test_get_my_instructor_projectlist(self):
        client = Client()

        self.assertTrue(
            client.login(username='test_student_one', password='test'))

        response = client.get('/yourspace/projects/test_instructor_two/',
                              {},
                              HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        json = simplejson.loads(response.content)

        assignments = json['assignments']
        self.assertEquals(len(assignments), 0)

        projects = json['projects']
        self.assertEquals(len(projects), 1)
        self.assertProjectEquals(projects[0],
                                 'Sample Course Assignment',
                                 'test_instructor_two',
                                 False)

    def test_get_my_peer_projectlist(self):
        client = Client()

        self.assertTrue(
            client.login(username='test_student_two', password='test'))

        response = client.get('/yourspace/projects/test_student_one/',
                              {},
                              HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        json = simplejson.loads(response.content)
        assignments = json['assignments']
        self.assertEquals(len(assignments), 0)

        projects = json['projects']
        self.assertEquals(len(projects), 1)

        self.assertProjectEquals(projects[0],
                                 'Public To Class Composition',
                                 'Student One',
                                 False)

    def test_get_my_projectlist_as_instructor(self):
        client = Client()

        self.assertTrue(
            client.login(username='test_instructor_two', password='test'))

        response = client.get('/?set_course=Sample_Course_Students')
        self.assertEquals(response.status_code, 200)

        response = client.get('/yourspace/projects/test_instructor_two/',
                              {},
                              HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        json = simplejson.loads(response.content)

        assignments = json['assignments']
        self.assertEquals(len(assignments), 0)

        projects = json['projects']
        self.assertEquals(len(projects), 1)
        self.assertProjectEquals(projects[0],
                                 'Sample Course Assignment',
                                 'test_instructor_two',
                                 True)

    def test_instructor_projectlist_as_instructor_two(self):
        client = Client()

        self.assertTrue(
            client.login(username='test_instructor_two', password='test'))

        response = client.get('/?set_course=Sample_Course_Students')
        self.assertEquals(response.status_code, 200)

        response = client.get('/yourspace/projects/test_instructor/',
                              {},
                              HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        json = simplejson.loads(response.content)

        self.assertEquals(len(json['assignments']), 0)
        # The assignment is viewable here.

        self.assertEquals(len(json['projects']), 0)

    def test_get_student_projectlist_as_instructor(self):
        client = Client()

        self.assertTrue(
            client.login(username='test_instructor', password='test'))

        response = client.get('/yourspace/projects/test_student_one/',
                              {},
                              HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        json = simplejson.loads(response.content)
        self.assertEquals(len(json['assignments']), 0)

        projects = json['projects']
        self.assertEquals(len(projects), 2)

        self.assertProjectEquals(projects[0],
                                 'Public To Class Composition',
                                 'Student One',
                                 False)

        self.assertProjectEquals(projects[1],
                                 'Instructor Shared',
                                 'Student One',
                                 False)

    def test_request_nonclassmember_projectlist(self):
        client = Client()

        self.assertTrue(
            client.login(username='test_student_one', password='test'))

        response = client.get('/yourspace/projects/test_student_alt/',
                              {},
                              HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEquals(response.status_code, 404)

        response = client.get('/yourspace/projects/test_instructor_alt/',
                              {},
                              HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEquals(response.status_code, 404)

    def test_get_all_projects_as_student(self):
        client = Client()

        self.assertTrue(
            client.login(username='test_student_one', password='test'))

        response = client.get('/yourspace/projects/',
                              {},
                              HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        json = simplejson.loads(response.content)
        self.assertTrue('assignments' not in json)

        projects = json['projects']
        self.assertEquals(len(projects), 4)

        self.assertProjectEquals(projects[0],
                                 'Sample Course Assignment',
                                 'test_instructor_two',
                                 False)

        self.assertProjectEquals(projects[1],
                                 'Public To Class Composition',
                                 'Student One',
                                 False)

        self.assertProjectEquals(projects[2],
                                 'Instructor Shared',
                                 'Student One',
                                 False)

        self.assertProjectEquals(projects[3],
                                 'Private Composition',
                                 'Student One',
                                 False)

    def test_get_all_projects_as_peer(self):
        client = Client()

        self.assertTrue(
            client.login(username='test_student_two', password='test'))

        response = client.get('/yourspace/projects/',
                              {},
                              HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        json = simplejson.loads(response.content)
        self.assertTrue('assignments' not in json)

        projects = json['projects']
        self.assertEquals(len(projects), 2)
        self.assertProjectEquals(projects[0],
                                 'Sample Course Assignment',
                                 'test_instructor_two',
                                 False)
        self.assertProjectEquals(projects[1],
                                 'Public To Class Composition',
                                 'Student One',
                                 False)

    def test_get_all_projects_as_instructor(self):
        client = Client()

        self.assertTrue(
            client.login(username='test_instructor', password='test'))

        response = client.get('/yourspace/projects/',
                              {},
                              HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        json = simplejson.loads(response.content)
        self.assertTrue('assignments' not in json)

        projects = json['projects']
        self.assertEquals(len(projects), 3)
        self.assertProjectEquals(projects[0],
                                 'Sample Course Assignment',
                                 'test_instructor_two',
                                 False)
        self.assertProjectEquals(projects[1],
                                 'Public To Class Composition',
                                 'Student One',
                                 False)
        self.assertProjectEquals(projects[2],
                                 'Instructor Shared',
                                 'Student One',
                                 False)
