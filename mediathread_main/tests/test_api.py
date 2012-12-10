from courseaffils.models import Course
from mediathread_main import course_details
from tastypie.test import ResourceTestCase


class CourseResourceTest(ResourceTestCase):
    # Use ``fixtures`` & ``urls`` as normal. See Django's ``TestCase``
    # documentation for the gory details.
    fixtures = ['unittest_sample_course.json',
                'unittest_sample_projects.json']

    def assertAssetEquals(self, asset, title, author,
                          primary_type, selection_ids, thumb_url):

        self.assertEquals(asset['title'], title)
        self.assertEquals(asset['author']['full_name'], author)
        self.assertEquals(asset['primary_type'], primary_type)
        self.assertEquals(asset['thumb_url'], thumb_url)

        self.assertEquals(len(asset['selections']), len(selection_ids))

        for idx, s in enumerate(asset['selections']):
            self.assertEquals(int(s['id']), selection_ids[idx])

    def assertProjectEquals(self, project, title, author, selection_ids):
        self.assertEquals(project['title'], title)
        self.assertEquals(project['attribution'], author)

        self.assertEquals(len(project['selections']), len(selection_ids))
        for idx, s in enumerate(project['selections']):
            self.assertEquals(int(s['id']), selection_ids[idx])

    def test_student_getobject_facultygroup(self):
        self.assertTrue(
            self.api_client.client.login(username="test_student_one",
                                         password="test"))

        response = self.api_client.get('/_main/api/v1/course/1/',
                                       format='json')

        self.assertValidJSONResponse(response)

        json = self.deserialize(response)

        faculty = ['Instructor One', 'test_instructor_two']

        self.assertTrue(json['faculty_group']['user_set'][0]['full_name']
                        in faculty)

        self.assertTrue(json['faculty_group']['user_set'][1]['full_name']
                        in faculty)

    def test_student_getobject(self):
        self.assertTrue(
            self.api_client.client.login(username="test_student_one",
                                         password="test"))

        response = self.api_client.get('/_main/api/v1/course/1/',
                                       format='json')

        self.assertValidJSONResponse(response)

        json = self.deserialize(response)

        objects = json['item_set']
        self.assertAssetEquals(objects[0], 'Mediathread: Introduction',
                               'Instructor One', 'youtube', [2, 3, 17],
                               'http://i.ytimg.com/vi/7KjzRG8zYYo/default.jpg')

        self.assertAssetEquals(
            objects[1], 'MAAP Award Reception',
            'Instructor One', 'image', [5, 8, 9, 10],
            'http://localhost:8002/site_media/img/test/maap_thumb.jpg')

        self.assertAssetEquals(
            objects[2],
            'The Armory - Home to CCNMTL\'S CUMC Office',
            'Instructor One', 'image', [7],
            'http://localhost:8002/site_media/img/test/armory_thumb.jpg')

        objects = json['project_set']
        self.assertProjectEquals(objects[0], 'Private Composition',
                                 'Student One', [8, 10])

        self.assertProjectEquals(objects[1], 'Instructor Shared',
                                 'Student One', [])

        self.assertProjectEquals(objects[2], 'Public To Class Composition',
                                 'Student One', [2, 5, 7])

    def test_student_getobject_restricted(self):
        # Set course details to restricted
        sample_course = Course.objects.get(title="Sample Course")
        sample_course.add_detail(course_details.SELECTION_VISIBILITY_KEY, 0)

        self.assertTrue(
            self.api_client.client.login(username="test_student_one",
                                         password="test"))

        response = self.api_client.get('/_main/api/v1/course/1/',
                                       format='json')

        self.assertValidJSONResponse(response)

        json = self.deserialize(response)

        objects = json['item_set']
        self.assertAssetEquals(objects[0], 'Mediathread: Introduction',
                               'Instructor One', 'youtube', [2, 3, 17],
                               'http://i.ytimg.com/vi/7KjzRG8zYYo/default.jpg')

        self.assertAssetEquals(
            objects[1], 'MAAP Award Reception',
            'Instructor One', 'image', [5, 8, 9],
            'http://localhost:8002/site_media/img/test/maap_thumb.jpg')

        self.assertAssetEquals(
            objects[2],
            'The Armory - Home to CCNMTL\'S CUMC Office',
            'Instructor One', 'image', [7],
            'http://localhost:8002/site_media/img/test/armory_thumb.jpg')

        objects = json['project_set']
        self.assertProjectEquals(objects[0], 'Private Composition',
                                 'Student One', [8, 10])

        self.assertProjectEquals(objects[1], 'Instructor Shared',
                                 'Student One', [])

        self.assertProjectEquals(objects[2], 'Public To Class Composition',
                                 'Student One', [2, 5, 7])

    def test_instructor_getobject(self):
        self.assertTrue(
            self.api_client.client.login(username="test_instructor",
                                         password="test"))

        response = self.api_client.get('/_main/api/v1/course/1/',
                                       format='json')

        self.assertValidJSONResponse(response)

        json = self.deserialize(response)

        objects = json['item_set']
        self.assertAssetEquals(objects[0], 'Mediathread: Introduction',
                               'Instructor One', 'youtube', [1, 2, 3, 17],
                               'http://i.ytimg.com/vi/7KjzRG8zYYo/default.jpg')

        self.assertAssetEquals(
            objects[1], 'MAAP Award Reception',
            'Instructor One', 'image', [4, 5, 8, 10],
            'http://localhost:8002/site_media/img/test/maap_thumb.jpg')

        self.assertAssetEquals(
            objects[2],
            'The Armory - Home to CCNMTL\'S CUMC Office',
            'Instructor One', 'image', [6, 7],
            'http://localhost:8002/site_media/img/test/armory_thumb.jpg')

        objects = json['project_set']
        self.assertProjectEquals(objects[0], 'Instructor Shared',
                                 'Student One', [])

        self.assertProjectEquals(objects[1], 'Public To Class Composition',
                                 'Student One', [2, 5, 7])

    def test_instructor_getobject_restricted(self):
        # Set course details to restricted
        sample_course = Course.objects.get(title="Sample Course")
        sample_course.add_detail(course_details.SELECTION_VISIBILITY_KEY, 0)

        self.test_instructor_getobject()

    def test_nonclassmember_getobject(self):
        self.assertTrue(
            self.api_client.client.login(username="test_instructor",
                                         password="test"))

        response = self.api_client.get('/_main/api/v1/course/2/',
                                       format='json')

        self.assertEqual(response.status_code, 404)

    def test_get_list(self):
        self.assertTrue(
            self.api_client.client.login(username="test_instructor",
                                         password="test"))

        self.assertHttpMethodNotAllowed(self.api_client.get(
            '/_main/api/v1/course/', format='json'))

    def test_post_list(self):
        self.assertTrue(
            self.api_client.client.login(username="test_instructor",
                                         password="test"))

        self.assertHttpMethodNotAllowed(self.api_client.post(
            '/_main/api/v1/course/', format='json', data={}))

    def test_put_detail(self):
        self.assertTrue(
            self.api_client.client.login(username="test_instructor",
                                         password="test"))

        self.assertHttpMethodNotAllowed(self.api_client.put(
            '/_main/api/v1/asset/2/', format='json', data={}))

    def test_delete(self):
        self.assertTrue(
            self.api_client.client.login(username="test_instructor",
                                         password="test"))

        self.assertHttpMethodNotAllowed(self.api_client.delete(
            '/_main/api/v1/asset/2/', format='json'))
