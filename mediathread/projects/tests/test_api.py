# pylint: disable-msg=R0904
# pylint: disable-msg=E1103
import json

from django.test.testcases import TestCase

from mediathread.factories import MediathreadTestMixin, UserFactory, \
    AssetFactory, SherdNoteFactory, ProjectFactory


class ProjectApiTest(MediathreadTestMixin, TestCase):

    def get_credentials(self):
        return None

    def assertProjectEquals(self, project, title, author, selection_ids=None):
        self.assertEquals(project['title'], title)
        self.assertEquals(project['attribution'], author)

    def assertSelectionsEqual(self, selections, selection_ids):
        self.assertEquals(len(selections), len(selection_ids))
        for idx, selection in enumerate(selections):
            self.assertEquals(int(selection['id']), selection_ids[idx])

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
        self.project_class_shared = ProjectFactory.create(
            course=self.sample_course, author=self.student_one,
            policy='CourseProtected')

        self.assignment = ProjectFactory.create(
            course=self.sample_course, author=self.instructor_one,
            policy='Assignment')

        # Alt Course Projects
        self.project_private_alt_course = ProjectFactory.create(
            course=self.sample_course, author=self.student_one,
            policy='PrivateEditorsAreOwners')

        self.project_public_alt_course = ProjectFactory.create(
            course=self.sample_course, author=self.student_one,
            policy='PrivateEditorsAreOwners')

    def test_student_one_getlist(self):
        self.assertTrue(self.client.login(username=self.student_one.username,
                                          password="test"))

        response = self.client.get('/api/project/', {},
                                   HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        the_json = json.loads(response.content)
        projects = the_json['projects']
        self.assertEquals(len(projects), 4)

        self.assertProjectEquals(projects[0], self.assignment.title,
                                 'Instructor One')

        self.assertProjectEquals(projects[1], self.project_class_shared.title,
                                 'Student One')

        self.assertProjectEquals(projects[2],
                                 self.project_instructor_shared.title,
                                 'Student One')

        self.assertProjectEquals(projects[3],
                                 self.project_private.title,
                                 'Student One')

    def test_student_two_getlist(self):
        self.assertTrue(self.client.login(username=self.student_two.username,
                                          password="test"))

        response = self.client.get('/api/project/', {},
                                   HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEquals(response.status_code, 200)

        the_json = json.loads(response.content)
        projects = the_json['projects']
        self.assertEquals(len(projects), 2)

        self.assertProjectEquals(projects[0], self.assignment.title,
                                 'Instructor One')

        self.assertProjectEquals(projects[1], self.project_class_shared.title,
                                 'Student One')

    def test_student_two_getlist_filtered(self):
        self.assertTrue(
            self.client.login(username=self.student_two.username,
                              password="test"))

        url = '/api/project/user/%s/' % self.student_two.username
        response = self.client.get(url, {},
                                   HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEquals(response.status_code, 200)

        the_json = json.loads(response.content)
        projects = the_json['projects']
        self.assertEquals(len(projects), 0)

    def test_instructor_getlist(self):
        self.assertTrue(
            self.client.login(username=self.instructor_one.username,
                              password="test"))

        response = self.client.get('/api/project/',
                                   {},
                                   HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEquals(response.status_code, 200)

        the_json = json.loads(response.content)
        projects = the_json['projects']
        self.assertEquals(len(projects), 3)

        self.assertProjectEquals(projects[0], self.assignment.title,
                                 'Instructor One')

        self.assertProjectEquals(projects[1], self.project_class_shared.title,
                                 'Student One')

        self.assertProjectEquals(projects[2],
                                 self.project_instructor_shared.title,
                                 'Student One')

    def test_student_one_getobject(self):
        self.assertTrue(self.client.login(username=self.student_one.username,
                                          password="test"))

        # My own private composition
        url = '/api/project/%s/' % self.project_private.id
        response = self.client.get(url, {},
                                   HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEquals(response.status_code, 200)

        the_json = json.loads(response.content)

        self.assertProjectEquals(the_json['project'],
                                 self.project_private.title,
                                 'Student One')
        self.assertSelectionsEqual(json['annotations'],
                                   [self.student_note.id, self.student_ga.id])

    def test_student_one_getobject_altcourse(self):
        self.assertTrue(self.client.login(username=self.student_one.username,
                                          password="test"))

        # Student three composition in alt course
        url = '/api/project/%s/' % self.project_alt_course.id
        response = self.api_client.get(url, {},
                                       HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 403)

    def test_student_two_getobject(self):
        self.assertTrue(
            self.client.login(username="test_student_two",
                                         password="test"))

        # Student one private composition
        response = self.api_client.get('/api/project/1/',
                                       format='json',
                                       HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 403)

        # Student one instructor shared composition
        response = self.api_client.get('/api/project/2/',
                                       format='json',
                                       HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 403)

        # Student one public to class composition
        response = self.api_client.get('/api/project/3/',
                                       format='json',
                                       HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEquals(response.status_code, 200)
        the_json = json.loads(response.content)
        self.assertProjectEquals(json['project'],
                                 'Public To Class Composition',
                                 'Student One')
        self.assertSelectionsEqual(json['annotations'], [2, 5, 7])

        # Student three composition in alt course
        response = self.api_client.get('/api/project/4/',
                                       format='json',
                                       HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 403)

    def test_instructor_getobject(self):
        self.assertTrue(
            self.client.login(username=self.instructor_one.username,
                              password="test"))

        # Student one private composition
        response = self.api_client.get('/api/project/1/',
                                       format='json',
                                       HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 403)

        # Student one instructor shared composition
        response = self.api_client.get('/api/project/2/',
                                       format='json',
                                       HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEquals(response.status_code, 200)
        the_json = json.loads(response.content)
        self.assertProjectEquals(json['project'], 'Instructor Shared',
                                 'Student One')
        self.assertEquals(len(json['annotations']), 0)

        # Student one public to class composition
        response = self.api_client.get('/api/project/3/',
                                       format='json',
                                       HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEquals(response.status_code, 200)
        the_json = json.loads(response.content)
        self.assertProjectEquals(json['project'],
                                 'Public To Class Composition', 'Student One')
        self.assertSelectionsEqual(json['annotations'], [2, 5, 7])

        # Student three composition in alt course
        response = self.api_client.get('/api/project/4/',
                                       format='json',
                                       HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 403)

    def test_post_list(self):
        self.assertTrue(
            self.client.login(username=self.instructor_one.username,
                              password="test"))

        response = self.client.post('/api/project/',
                                    {},
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEquals(response.status_code, 405)

    def test_put_detail(self):
        self.assertTrue(
            self.client.login(username=self.instructor_one.username,
                              password="test"))

        response = self.client.put('/api/project/2/',
                                   data={},
                                   HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        self.assertEquals(response.status_code, 405)

    def test_delete(self):
        self.assertTrue(
            self.client.login(username=self.instructor_one.username,
                              password="test"))
        response = self.client.delete('/api/project/2/',
                                      data={},
                                      HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEquals(response.status_code, 405)
