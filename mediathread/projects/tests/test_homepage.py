# pylint: disable-msg=R0904
# pylint: disable-msg=E1103
import json

from django.test import TestCase

from mediathread.factories import MediathreadTestMixin, UserFactory, \
    AssetFactory, SherdNoteFactory, ProjectFactory


class HomepageTest(MediathreadTestMixin, TestCase):

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
            title=None, is_global_annotation=True)
        self.instructor_note = SherdNoteFactory(
            asset=self.asset1, author=self.instructor_one,
            tags=',image, instructor_one_selection,',
            body='instructor one selection note', range1=0, range2=1)
        self.instructor_ga = SherdNoteFactory(
            asset=self.asset1, author=self.instructor_one,
            tags=',image, instructor_one_item,',
            body='instructor one item note',
            title=None, is_global_annotation=True)

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
            policy='CourseProtected', project_type='assignment')

        # Alt Course Projects
        self.project_private_alt_course = ProjectFactory.create(
            course=self.alt_course, author=self.alt_student,
            policy='PrivateEditorsAreOwners')

        self.project_public_alt_course = ProjectFactory.create(
            course=self.alt_course, author=self.alt_student,
            policy='PrivateEditorsAreOwners')

    def assertProjectEquals(self, project, title, author, editable):
        self.assertEquals(project['title'], title)
        self.assertEquals(project['participants'][0]['public_name'], author)
        self.assertEquals(project['editable'], editable)

    def test_get_my_projectlist_as_student(self):
        self.assertTrue(self.client.login(username=self.student_one.username,
                                          password='test'))

        url = '/api/project/user/%s/' % self.student_one.username
        response = self.client.get(url, {},
                                   HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        the_json = json.loads(response.content)

        assignments = the_json['assignments']
        self.assertEquals(len(assignments), 1)
        self.assertEquals(assignments[0]['title'], self.assignment.title)
        self.assertTrue(assignments[0]['display_as_assignment'])
        self.assertFalse(assignments[0]['is_faculty'])

        projects = the_json['projects']
        self.assertEquals(len(projects), 3)

        self.assertProjectEquals(projects[0], self.project_class_shared.title,
                                 'Student One', True)

        self.assertProjectEquals(projects[1],
                                 self.project_instructor_shared.title,
                                 'Student One', True)

        self.assertProjectEquals(projects[2], self.project_private.title,
                                 'Student One', True)

    def test_get_my_instructor_projectlist(self):
        self.assertTrue(self.client.login(username=self.student_one.username,
                                          password='test'))

        url = '/api/project/user/%s/' % self.instructor_one.username

        response = self.client.get(url, {},
                                   HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        the_json = json.loads(response.content)

        assignments = the_json['assignments']
        self.assertEquals(len(assignments), 0)

        projects = the_json['projects']
        self.assertEquals(len(projects), 1)
        self.assertProjectEquals(projects[0], self.assignment.title,
                                 'Instructor One', False)

    def test_get_my_peer_projectlist(self):
        self.assertTrue(self.client.login(username=self.student_two.username,
                                          password='test'))

        url = '/api/project/user/%s/' % self.student_one.username
        response = self.client.get(url, {},
                                   HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        the_json = json.loads(response.content)
        assignments = the_json['assignments']
        self.assertEquals(len(assignments), 0)

        projects = the_json['projects']
        self.assertEquals(len(projects), 1)

        self.assertProjectEquals(projects[0], self.project_class_shared.title,
                                 'Student One', False)

    def test_get_my_projectlist_as_instructor(self):
        self.assertTrue(
            self.client.login(username=self.instructor_one.username,
                              password='test'))
        self.switch_course(self.client, self.sample_course)

        url = '/api/project/user/%s/' % self.instructor_one.username
        response = self.client.get(url, {},
                                   HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        the_json = json.loads(response.content)

        assignments = the_json['assignments']
        self.assertEquals(len(assignments), 0)

        projects = the_json['projects']
        self.assertEquals(len(projects), 1)
        self.assertProjectEquals(projects[0], self.assignment.title,
                                 'Instructor One', True)

    def test_instructor_projectlist_as_instructor_two(self):
        self.assertTrue(
            self.client.login(username=self.instructor_two.username,
                              password='test'))
        self.switch_course(self.client, self.sample_course)

        url = '/api/project/user/%s/' % self.instructor_one.username
        response = self.client.get(url, {},
                                   HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        the_json = json.loads(response.content)

        self.assertEquals(len(the_json['assignments']), 0)

        # The assignment is viewable here.
        self.assertEquals(len(the_json['projects']), 1)
        self.assertProjectEquals(the_json['projects'][0],
                                 self.assignment.title,
                                 'Instructor One', False)

    def test_get_student_projectlist_as_instructor(self):
        self.assertTrue(
            self.client.login(username=self.instructor_one.username,
                              password='test'))
        self.switch_course(self.client, self.sample_course)

        url = '/api/project/user/%s/' % self.student_one.username
        response = self.client.get(url, {},
                                   HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        the_json = json.loads(response.content)
        self.assertEquals(len(the_json['assignments']), 0)

        projects = the_json['projects']
        self.assertEquals(len(projects), 2)

        self.assertProjectEquals(projects[0], self.project_class_shared.title,
                                 'Student One', False)

        self.assertProjectEquals(projects[1],
                                 self.project_instructor_shared.title,
                                 'Student One', False)

    def test_request_nonclassmember_projectlist(self):
        self.client.login(username=self.student_one.username, password='test')

        url = '/api/project/user/%s/' % self.alt_student.username
        response = self.client.get(url, {},
                                   HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEquals(response.status_code, 200)
        the_json = json.loads(response.content)
        self.assertFalse('compositions' in the_json)

        url = '/api/project/user/%s/' % self.alt_instructor.username
        response = self.client.get(url, {},
                                   HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEquals(response.status_code, 200)
        self.assertFalse('compositions' in the_json)

    def test_request_superuser_nonclassmember_projectlist(self):
        su = UserFactory(is_staff=True, is_superuser=True)
        self.client.login(username=su.username, password='test')
        self.switch_course(self.client, self.sample_course)

        url = '/api/project/user/%s/' % su.username
        response = self.client.get(url, {},
                                   HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEquals(response.status_code, 200)
        the_json = json.loads(response.content)
        self.assertFalse('compositions' in the_json)

    def test_get_all_projects_as_student(self):
        self.assertTrue(
            self.client.login(username=self.student_one.username,
                              password='test'))

        response = self.client.get('/api/project/', {},
                                   HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        the_json = json.loads(response.content)
        self.assertEquals(the_json['assignments'], [])

        projects = the_json['projects']
        self.assertEquals(len(projects), 4)

        self.assertProjectEquals(projects[0], self.assignment.title,
                                 'Instructor One', False)

        self.assertProjectEquals(projects[1], self.project_class_shared.title,
                                 'Student One', False)

        self.assertProjectEquals(projects[2],
                                 self.project_instructor_shared.title,
                                 'Student One', False)

        self.assertProjectEquals(projects[3], self.project_private.title,
                                 'Student One', False)

    def test_get_all_projects_as_peer(self):
        self.assertTrue(
            self.client.login(username=self.student_two.username,
                              password='test'))

        response = self.client.get('/api/project/', {},
                                   HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        the_json = json.loads(response.content)
        self.assertEquals(the_json['assignments'], [])

        projects = the_json['projects']
        self.assertEquals(len(projects), 2)
        self.assertProjectEquals(projects[0], self.assignment.title,
                                 'Instructor One', False)

        self.assertProjectEquals(projects[1], self.project_class_shared.title,
                                 'Student One', False)

    def test_get_all_projects_as_instructor(self):
        self.assertTrue(
            self.client.login(username=self.instructor_one.username,
                              password='test'))
        self.switch_course(self.client, self.sample_course)

        response = self.client.get('/api/project/', {},
                                   HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        the_json = json.loads(response.content)
        self.assertEquals(the_json['assignments'], [])

        projects = the_json['projects']
        self.assertProjectEquals(projects[0], self.assignment.title,
                                 'Instructor One', False)

        self.assertProjectEquals(projects[1], self.project_class_shared.title,
                                 'Student One', False)

        self.assertProjectEquals(projects[2],
                                 self.project_instructor_shared.title,
                                 'Student One', False)
