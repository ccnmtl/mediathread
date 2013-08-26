from tastypie.test import ResourceTestCase


class ProjectResourceTest(ResourceTestCase):
    # Use ``fixtures`` & ``urls`` as normal. See Django's ``TestCase``
    # documentation for the gory details.
    fixtures = ['unittest_sample_course.json',
                'unittest_sample_projects.json']

    def assertProjectEquals(self, project, title, author, selection_ids):
        self.assertEquals(project['title'], title)
        self.assertEquals(project['attribution'], author)

        self.assertEquals(len(project['annotations']), len(selection_ids))
        for idx, s in enumerate(project['annotations']):
            self.assertEquals(int(s['id']), selection_ids[idx])

    def test_student_one_getlist(self):
        self.assertTrue(
            self.api_client.client.login(username="test_student_one",
                                         password="test"))

        response = self.api_client.get('/_main/api/v1/project/',
                                       format='json')
        self.assertValidJSONResponse(response)

        json = self.deserialize(response)
        objects = json['objects']
        self.assertEquals(len(objects), 4)

        self.assertProjectEquals(objects[0], 'Private Composition',
                                 'Student One', [8, 10])

        self.assertProjectEquals(objects[1], 'Instructor Shared',
                                 'Student One', [])

        self.assertProjectEquals(objects[2], 'Public To Class Composition',
                                 'Student One', [2, 5, 7])

        self.assertProjectEquals(objects[3], 'Sample Course Assignment',
                                 'test_instructor_two', [1, 10, 18, 19, 20])

    def test_student_two_getlist(self):
        self.assertTrue(
            self.api_client.client.login(username="test_student_two",
                                         password="test"))

        response = self.api_client.get('/_main/api/v1/project/',
                                       format='json')
        self.assertValidJSONResponse(response)

        json = self.deserialize(response)
        objects = json['objects']
        self.assertEquals(len(objects), 2)

        self.assertProjectEquals(objects[0], 'Public To Class Composition',
                                 'Student One', [2, 5, 7])

        self.assertProjectEquals(objects[1], 'Sample Course Assignment',
                                 'test_instructor_two', [1, 10, 18, 19, 20])

    def test_student_two_getlist_filtered(self):
        self.assertTrue(
            self.api_client.client.login(username="test_student_two",
                                         password="test"))

        response = self.api_client.get('/_main/api/v1/project/?author__id=4',
                                       format='json')
        self.assertValidJSONResponse(response)

        json = self.deserialize(response)
        objects = json['objects']
        self.assertEquals(len(objects), 0)

    def test_instructor_getlist(self):
        self.assertTrue(
            self.api_client.client.login(username="test_instructor",
                                         password="test"))

        response = self.api_client.get('/_main/api/v1/project/',
                                       format='json')
        self.assertValidJSONResponse(response)

        json = self.deserialize(response)
        objects = json['objects']
        self.assertEquals(len(objects), 3)

        self.assertProjectEquals(objects[0], 'Instructor Shared',
                                 'Student One', [])

        self.assertProjectEquals(objects[1], 'Public To Class Composition',
                                 'Student One', [2, 5, 7])

        self.assertProjectEquals(objects[2], 'Sample Course Assignment',
                                 'test_instructor_two', [1, 10, 18, 19, 20])

    def test_student_one_getobject(self):
        self.assertTrue(
            self.api_client.client.login(username="test_student_one",
                                         password="test"))

        # My own private composition
        response = self.api_client.get('/_main/api/v1/project/1/',
                                       format='json')
        self.assertValidJSONResponse(response)

        json = self.deserialize(response)

        self.assertProjectEquals(json, 'Private Composition',
                                 'Student One', [8, 10])

        # Student three composition in alt course
        response = self.api_client.get('/_main/api/v1/project/4/',
                                       format='json')
        self.assertEqual(response.status_code, 404)

    def test_student_two_getobject(self):
        self.assertTrue(
            self.api_client.client.login(username="test_student_two",
                                         password="test"))

        # Student one private composition
        response = self.api_client.get('/_main/api/v1/project/1/',
                                       format='json')
        self.assertEqual(response.status_code, 404)

        # Student one instructor shared composition
        response = self.api_client.get('/_main/api/v1/project/2/',
                                       format='json')
        self.assertEqual(response.status_code, 404)

        # Student one public to class composition
        response = self.api_client.get('/_main/api/v1/project/3/',
                                       format='json')
        self.assertValidJSONResponse(response)
        json = self.deserialize(response)
        self.assertProjectEquals(json, 'Public To Class Composition',
                                 'Student One', [2, 5, 7])

        # Student three composition in alt course
        response = self.api_client.get('/_main/api/v1/project/4/',
                                       format='json')
        self.assertEqual(response.status_code, 404)

    def test_instructor_getobject(self):
        self.assertTrue(
            self.api_client.client.login(username="test_instructor",
                                         password="test"))

        # Student one private composition
        response = self.api_client.get('/_main/api/v1/project/1/',
                                       format='json')
        self.assertEqual(response.status_code, 404)

        # Student one instructor shared composition
        response = self.api_client.get('/_main/api/v1/project/2/',
                                       format='json')
        self.assertValidJSONResponse(response)
        json = self.deserialize(response)
        self.assertProjectEquals(json, 'Instructor Shared',
                                 'Student One', [])

        # Student one public to class composition
        response = self.api_client.get('/_main/api/v1/project/3/',
                                       format='json')
        self.assertValidJSONResponse(response)
        json = self.deserialize(response)
        self.assertProjectEquals(json, 'Public To Class Composition',
                                 'Student One', [2, 5, 7])

        # Student three composition in alt course
        response = self.api_client.get('/_main/api/v1/project/4/',
                                       format='json')
        self.assertEqual(response.status_code, 404)

    def test_post_list(self):
        self.assertTrue(
            self.api_client.client.login(username="test_instructor",
                                         password="test"))

        self.assertHttpMethodNotAllowed(self.api_client.post(
            '/_main/api/v1/project/', format='json', data={}))

    def test_put_detail(self):
        self.assertTrue(
            self.api_client.client.login(username="test_instructor",
                                         password="test"))

        self.assertHttpMethodNotAllowed(self.api_client.put(
            '/_main/api/v1/project/2/', format='json', data={}))

    def test_delete(self):
        self.assertTrue(
            self.api_client.client.login(username="test_instructor",
                                         password="test"))

        self.assertHttpMethodNotAllowed(self.api_client.delete(
            '/_main/api/v1/project/2/', format='json'))
