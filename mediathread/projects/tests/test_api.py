#pylint: disable-msg=R0904
#pylint: disable-msg=E1103
from tastypie.test import ResourceTestCase


class ProjectApiTest(ResourceTestCase):
    # Use ``fixtures`` & ``urls`` as normal. See Django's ``TestCase``
    # documentation for the gory details.
    fixtures = ['unittest_sample_course.json',
                'unittest_sample_projects.json']

    def get_credentials(self):
        return None

    def assertProjectEquals(self, project, title, author, selection_ids=None):
        self.assertEquals(project['title'], title)
        self.assertEquals(project['attribution'], author)

    def assertSelectionsEqual(self, selections, selection_ids):
        self.assertEquals(len(selections), len(selection_ids))
        for idx, selection in enumerate(selections):
            self.assertEquals(int(selection['id']), selection_ids[idx])

    def test_student_one_getlist(self):
        self.assertTrue(
            self.api_client.client.login(username="test_student_one",
                                         password="test"))

        response = self.api_client.get('/api/project/', format='json',
                                       HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertValidJSONResponse(response)

        json = self.deserialize(response)
        projects = json['projects']
        self.assertEquals(len(projects), 4)

        self.assertProjectEquals(projects[0], 'Sample Course Assignment',
                                 'test_instructor_two')

        self.assertProjectEquals(projects[1], 'Public To Class Composition',
                                 'Student One')

        self.assertProjectEquals(projects[2], 'Instructor Shared',
                                 'Student One')

        self.assertProjectEquals(projects[3], 'Private Composition',
                                 'Student One')

    def test_student_two_getlist(self):
        self.assertTrue(
            self.api_client.client.login(username="test_student_two",
                                         password="test"))

        response = self.api_client.get('/api/project/', format='json',
                                       HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertValidJSONResponse(response)

        json = self.deserialize(response)
        projects = json['projects']
        self.assertEquals(len(projects), 2)

        self.assertProjectEquals(projects[0], 'Sample Course Assignment',
                                 'test_instructor_two')

        self.assertProjectEquals(projects[1], 'Public To Class Composition',
                                 'Student One')

    def test_student_two_getlist_filtered(self):
        self.assertTrue(
            self.api_client.client.login(username="test_student_two",
                                         password="test"))

        response = self.api_client.get('/api/project/user/test_student_two/',
                                       format='json',
                                       HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertValidJSONResponse(response)

        json = self.deserialize(response)
        projects = json['projects']
        self.assertEquals(len(projects), 0)

    def test_instructor_getlist(self):
        self.assertTrue(
            self.api_client.client.login(username="test_instructor",
                                         password="test"))

        response = self.api_client.get('/api/project/',
                                       format='json',
                                       HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertValidJSONResponse(response)

        json = self.deserialize(response)
        projects = json['projects']
        self.assertEquals(len(projects), 3)

        self.assertProjectEquals(projects[0], 'Sample Course Assignment',
                                 'test_instructor_two')

        self.assertProjectEquals(projects[1], 'Public To Class Composition',
                                 'Student One')

        self.assertProjectEquals(projects[2], 'Instructor Shared',
                                 'Student One')

    def test_student_one_getobject(self):
        self.assertTrue(
            self.api_client.client.login(username="test_student_one",
                                         password="test"))

        # My own private composition
        response = self.api_client.get('/api/project/1/',
                                       format='json',
                                       HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertValidJSONResponse(response)

        json = self.deserialize(response)

        self.assertProjectEquals(json['project'], 'Private Composition',
                                 'Student One')
        self.assertSelectionsEqual(json['annotations'], [10, 8])

        # Student three composition in alt course
        response = self.api_client.get('/api/project/4/',
                                       format='json',
                                       HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 403)

    def test_student_two_getobject(self):
        self.assertTrue(
            self.api_client.client.login(username="test_student_two",
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
        self.assertValidJSONResponse(response)
        json = self.deserialize(response)
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
            self.api_client.client.login(username="test_instructor",
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
        self.assertValidJSONResponse(response)
        json = self.deserialize(response)
        self.assertProjectEquals(json['project'], 'Instructor Shared',
                                 'Student One')
        self.assertEquals(len(json['annotations']), 0)

        # Student one public to class composition
        response = self.api_client.get('/api/project/3/',
                                       format='json',
                                       HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertValidJSONResponse(response)
        json = self.deserialize(response)
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
            self.api_client.client.login(username="test_instructor",
                                         password="test"))

        self.assertHttpMethodNotAllowed(self.api_client.post(
            '/api/project/', format='json', data={}))

    def test_put_detail(self):
        self.assertTrue(
            self.api_client.client.login(username="test_instructor",
                                         password="test"))

        self.assertHttpMethodNotAllowed(self.api_client.put(
            '/api/project/2/', format='json', data={}))

    def test_delete(self):
        self.assertTrue(
            self.api_client.client.login(username="test_instructor",
                                         password="test"))

        self.assertHttpMethodNotAllowed(self.api_client.delete(
            '/api/project/2/', format='json'))
