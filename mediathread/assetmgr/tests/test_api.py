#pylint: disable-msg=R0904
#pylint: disable-msg=E1103
from courseaffils.models import Course
from datetime import datetime, timedelta
from mediathread.api import TagResource
from mediathread.assetmgr.models import Asset
from mediathread.main import course_details
from tagging.models import Tag
from tastypie.test import ResourceTestCase
import json


class AssetApiTest(ResourceTestCase):
    # Use ``fixtures`` & ``urls`` as normal. See Django's ``TestCase``
    # documentation for the gory details.
    fixtures = ['unittest_sample_course.json']

    def get_credentials(self):
        return None

    def assertAssetEquals(self, asset, title, author,
                          primary_type, selection_ids, thumb_url):

        self.assertEquals(asset['title'], title)
        self.assertEquals(asset['author']['public_name'], author)
        self.assertEquals(asset['primary_type'], primary_type)
        self.assertEquals(asset['thumb_url'], thumb_url)

        self.assertEquals(len(asset['annotations']), len(selection_ids))

        for idx, selection in enumerate(asset['annotations']):
            self.assertEquals(int(selection['id']), selection_ids[idx])

    def test_student_get_my_collection(self):
        username = "test_student_one"
        password = "test"
        self.assert_(self.client.login(username=username, password=password))

        response = self.client.get(
            "/api/asset/user/test_student_one/",
            {},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        the_json = json.loads(response.content)

        self.assertTrue(the_json['editable'])
        self.assertFalse(the_json['citable'])
        self.assertFalse(the_json['is_faculty'])
        self.assertEquals(len(the_json['assets']), 1)
        self.assertEquals(len(the_json['assets'][0]['annotations']), 0)

    def test_student_get_peer_collection(self):
        username = "test_student_one"
        password = "test"
        self.assert_(self.client.login(username=username, password=password))

        record_owner = 'test_student_two'
        response = self.client.get(
            "/api/asset/user/%s/?annotations=true" % record_owner,
            {},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        the_json = json.loads(response.content)

        self.assertFalse(the_json['editable'])
        self.assertFalse(the_json['citable'])
        self.assertFalse(the_json['is_faculty'])
        self.assertEquals(len(the_json['assets']), 1)
        self.assertEquals(len(the_json['assets'][0]['annotations']), 3)

        annotations = the_json['assets'][0]['annotations']
        self.assertEquals(annotations[0]['title'], 'Our esteemed leaders')
        self.assertEquals(annotations[1]['title'], 'The Award')
        self.assertEquals(annotations[2]['title'], 'Nice Tie')

        # student two's tags
        self.assertEquals(len(annotations[2]['metadata']['tags']), 1)
        self.assertEquals(annotations[2]['metadata']['body'],
                          "student two selection note")

        self.assertTrue('global_annotation' in the_json['assets'][0])
        gla = the_json['assets'][0]['global_annotation']
        self.assertEquals(len(gla['metadata']['tags']), 1)
        self.assertEquals(gla['metadata']['body'],
                          "student two item note")

    def test_student_getlist(self):
        self.assertTrue(
            self.api_client.client.login(username="test_student_one",
                                         password="test"))

        url = '/api/asset/?annotations=true'
        response = self.api_client.get(url, format='json',
                                       HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertValidJSONResponse(response)

        the_json = self.deserialize(response)
        objects = the_json['assets']
        self.assertEquals(len(objects), 4)

        self.assertAssetEquals(objects[0], 'Mediathread: Introduction',
                               'Instructor One', 'youtube', [2, 3, 17, 19],
                               'http://localhost:8002/media/img/test/'
                               'mediathread_introduction_thumb.jpg')

        self.assertAssetEquals(
            objects[1], 'Project Portfolio',
            'test_instructor_two', 'image', [], None)

        self.assertAssetEquals(
            objects[2], 'MAAP Award Reception',
            'Instructor One', 'image', [5, 8, 10],
            'http://localhost:8002/media/img/test/maap_thumb.jpg')

        self.assertAssetEquals(
            objects[3],
            'The Armory - Home to CCNMTL\'S CUMC Office',
            'Instructor One', 'image', [7],
            'http://localhost:8002/media/img/test/armory_thumb.jpg')

    def test_student_getlist_sorted(self):
        asset = Asset.objects.get(title='MAAP Award Reception')
        asset.modified = datetime.now() + timedelta(days=1)
        asset.save()

        self.assertTrue(
            self.api_client.client.login(username="test_student_one",
                                         password="test"))

        url = '/api/asset/?annotations=true'
        response = self.api_client.get(url, format='json',
                                       HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertValidJSONResponse(response)

        the_json = self.deserialize(response)
        objects = the_json['assets']
        self.assertEquals(len(objects), 4)

        self.assertAssetEquals(
            objects[0], 'MAAP Award Reception',
            'Instructor One', 'image', [5, 8, 10],
            'http://localhost:8002/media/img/test/maap_thumb.jpg')

        self.assertAssetEquals(objects[1], 'Mediathread: Introduction',
                               'Instructor One', 'youtube', [2, 3, 17, 19],
                               'http://localhost:8002/media/img/test/'
                               'mediathread_introduction_thumb.jpg')

    def test_student_getlist_restricted(self):
        # Set course details to restricted
        sample_course = Course.objects.get(title="Sample Course")
        sample_course.add_detail(course_details.SELECTION_VISIBILITY_KEY, 0)

        self.assertTrue(
            self.api_client.client.login(username="test_student_one",
                                         password="test"))

        url = '/api/asset/?annotations=true'
        response = self.api_client.get(url, format='json',
                                       HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertValidJSONResponse(response)

        the_json = self.deserialize(response)
        objects = the_json['assets']
        self.assertEquals(len(objects), 4)

        self.assertAssetEquals(objects[0], 'Mediathread: Introduction',
                               'Instructor One', 'youtube', [2, 3, 17, 19],
                               'http://localhost:8002/media/img/test/'
                               'mediathread_introduction_thumb.jpg')

        self.assertAssetEquals(
            objects[1],
            'Project Portfolio',
            'test_instructor_two', 'image', [],
            None)

        self.assertAssetEquals(
            objects[2], 'MAAP Award Reception',
            'Instructor One', 'image', [5, 8],
            'http://localhost:8002/media/img/test/maap_thumb.jpg')

        self.assertAssetEquals(
            objects[3],
            'The Armory - Home to CCNMTL\'S CUMC Office',
            'Instructor One', 'image', [7],
            'http://localhost:8002/media/img/test/armory_thumb.jpg')

    def test_student_getobject(self):
        self.assertTrue(
            self.api_client.client.login(username="test_student_one",
                                         password="test"))

        response = self.api_client.get('/api/asset/2/', format='json',
                                       HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertValidJSONResponse(response)
        the_json = self.deserialize(response)

        self.assertAssetEquals(
            the_json['assets']['2'], 'MAAP Award Reception',
            'Instructor One', 'image', [5, 8, 10],
            'http://localhost:8002/media/img/test/maap_thumb.jpg')

    def test_student_getobject_restricted(self):
        # Set course details to restricted
        sample_course = Course.objects.get(title="Sample Course")
        sample_course.add_detail(course_details.SELECTION_VISIBILITY_KEY, 0)

        self.assertTrue(
            self.api_client.client.login(username="test_student_one",
                                         password="test"))

        response = self.api_client.get('/api/asset/2/', format='json',
                                       HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertValidJSONResponse(response)
        the_json = self.deserialize(response)

        self.assertAssetEquals(
            the_json['assets']['2'], 'MAAP Award Reception',
            'Instructor One', 'image', [5, 8],
            'http://localhost:8002/media/img/test/maap_thumb.jpg')

    def test_instructor_getlist(self):
        self.assertTrue(
            self.api_client.client.login(username="test_instructor",
                                         password="test"))

        response = self.api_client.get('/api/asset/?annotations=true',
                                       format='json',
                                       HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertValidJSONResponse(response)

        the_json = self.deserialize(response)
        objects = the_json['assets']
        self.assertEquals(len(objects), 4)

        self.assertAssetEquals(objects[0], 'Mediathread: Introduction',
                               'Instructor One', 'youtube', [2, 3, 17, 19],
                               'http://localhost:8002/media/img/test/'
                               'mediathread_introduction_thumb.jpg')

        self.assertAssetEquals(
            objects[1],
            'Project Portfolio',
            'test_instructor_two', 'image', [],
            None)

        self.assertAssetEquals(
            objects[2], 'MAAP Award Reception',
            'Instructor One', 'image', [5, 8, 10],
            'http://localhost:8002/media/img/test/maap_thumb.jpg')

        self.assertAssetEquals(
            objects[3],
            'The Armory - Home to CCNMTL\'S CUMC Office',
            'Instructor One', 'image', [7],
            'http://localhost:8002/media/img/test/armory_thumb.jpg')

    def test_instructor_getlist_restricted(self):
        # Set course details to restricted
        sample_course = Course.objects.get(title="Sample Course")
        sample_course.add_detail(course_details.SELECTION_VISIBILITY_KEY, 0)

        self.test_instructor_getlist()

    def test_instructor_getobject(self):
        self.assertTrue(
            self.api_client.client.login(username="test_instructor",
                                         password="test"))

        response = self.api_client.get('/api/asset/1/', format='json',
                                       HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertValidJSONResponse(response)
        the_json = self.deserialize(response)

        self.assertAssetEquals(the_json['assets']['1'],
                               'Mediathread: Introduction',
                               'Instructor One', 'youtube', [2, 3, 17, 19],
                               'http://localhost:8002/media/img/test/'
                               'mediathread_introduction_thumb.jpg')

    def test_instructor_getobject_restricted(self):
        # Set course details to restricted
        sample_course = Course.objects.get(title="Sample Course")
        sample_course.add_detail(course_details.SELECTION_VISIBILITY_KEY, 0)

        self.test_instructor_getobject()

    def test_nonclassmember_getobject(self):
        # Student in Alternate Course attempts
        # to retrieve selections from Sample Course
        self.assertTrue(
            self.api_client.client.login(username="test_student_alt",
                                         password="test"))

        # Student One Selection
        response = self.api_client.get('/api/asset/1/',
                                       format='json',
                                       HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 404)

    def test_post_list(self):
        self.assertTrue(
            self.api_client.client.login(username="test_instructor",
                                         password="test"))

        self.assertHttpMethodNotAllowed(self.api_client.post(
            '/api/asset/', format='json', data={}))

    def test_put_detail(self):
        self.assertTrue(
            self.api_client.client.login(username="test_instructor",
                                         password="test"))

        self.assertHttpMethodNotAllowed(self.api_client.put(
            '/api/asset/2/', format='json', data={},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'))

    def test_delete(self):
        self.assertTrue(
            self.api_client.client.login(username="test_instructor",
                                         password="test"))

        self.assertHttpMethodNotAllowed(self.api_client.delete(
            '/api/asset/2/', format='json',
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'))

    def test_getobject_multiple_class_member_nocourse(self):
        self.assertTrue(
            self.api_client.client.login(username="test_student_three",
                                         password="test"))

        # No course selection yet
        response = self.api_client.get('/api/asset/1/',
                                       format='json',
                                       HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertHttpOK(response)
        self.assertEquals(response.templates[0].name,
                          "courseaffils/select_course.html")

    def test_getobject_multiple_class_member_wrongcourse(self):
        self.assertTrue(
            self.api_client.client.login(username="test_student_three",
                                         password="test"))

        response = self.api_client.client.get(
            '/?set_course=Alternate%20Course%20Members&next=/', follow=True)
        self.assertHttpOK(response)
        self.assertEquals(response.templates[0].name, "homepage.html")

        response = self.api_client.get('/api/asset/1/',
                                       format='json', follow=True,
                                       HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.templates[0].name,
                          "assetmgr/asset_not_found.html")

    def test_getobject_multiple_class_member_rightcourse(self):
        self.assertTrue(
            self.api_client.client.login(username="test_student_three",
                                         password="test"))

        response = self.api_client.client.get(
            '/?set_course=Sample_Course_Students', follow=True)
        self.assertHttpOK(response)
        self.assertEquals(response.templates[0].name, "homepage.html")
        response = self.api_client.get('/api/asset/1/',
                                       format='json',
                                       HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertHttpOK(response)
        self.assertValidJSONResponse(response)
        the_json = self.deserialize(response)
        self.assertAssetEquals(the_json['assets']['1'],
                               'Mediathread: Introduction',
                               'Instructor One', 'youtube', [2, 3, 17, 19],
                               'http://localhost:8002/media/img/test/'
                               'mediathread_introduction_thumb.jpg')

    def test_getlist_multiple_class_member(self):
        self.assertTrue(
            self.api_client.client.login(username="test_student_three",
                                         password="test"))

        # Student One Selection from Sample Course
        response = self.api_client.get('/api/asset/', format='json')
        self.assertHttpOK(response)
        self.assertEquals(response.templates[0].name,
                          "courseaffils/select_course.html")

        # No dice, login to Alternate Course
        response = self.api_client.client.get(
            '/?set_course=Alternate%20Course%20Members&next=/', follow=True)
        self.assertHttpOK(response)
        self.assertEquals(response.templates[0].name, "homepage.html")

        # Let's try this again -- asset list
        response = self.api_client.get('/api/asset/?annotations=true',
                                       format='json',
                                       HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        the_json = self.deserialize(response)
        objects = the_json['assets']
        self.assertEquals(len(objects), 1)

        self.assertAssetEquals(objects[0], 'Design Research',
                               'test_instructor_alt', 'image',
                               [13, 14, 15], None)


class TagApiTest(ResourceTestCase):
    fixtures = ['unittest_sample_course.json']

    def get_credentials(self):
        return None

    def test_render_list(self):
        asset = Asset.objects.get(id=1)
        tags = Tag.objects.usage_for_queryset(asset.sherdnote_set.all(),
                                              counts=True)
        resource = TagResource()
        lst = resource.render_list(None, tags)
        self.assertEquals(len(lst), 5)

        self.assertEquals(lst[0]['count'], 1)
        self.assertEquals(lst[0]['last'], False)
        self.assertEquals(lst[0]['name'], 'test_instructor_item')

        self.assertEquals(lst[4]['count'], 1)
        self.assertEquals(lst[4]['last'], True)
        self.assertEquals(lst[4]['name'], 'youtube')
