from courseaffils.models import Course
#from django.contrib.auth.models import User
#from mediathread.assetmgr.models import Asset
from mediathread.main import course_details
from tastypie.test import ResourceTestCase
#import datetime


class AssetResourceTest(ResourceTestCase):
    # Use ``fixtures`` & ``urls`` as normal. See Django's ``TestCase``
    # documentation for the gory details.
    fixtures = ['unittest_sample_course.json']

    def assertAssetEquals(self, asset, title, author,
                          primary_type, selection_ids, thumb_url):

        self.assertEquals(asset['title'], title)
        self.assertEquals(asset['author']['public_name'], author)
        self.assertEquals(asset['primary_type'], primary_type)
        self.assertEquals(asset['thumb_url'], thumb_url)

        self.assertEquals(len(asset['annotations']), len(selection_ids))

        for idx, s in enumerate(asset['annotations']):
            self.assertEquals(int(s['id']), selection_ids[idx])

    def test_student_getlist(self):
        self.assertTrue(
            self.api_client.client.login(username="test_student_one",
                                         password="test"))

        response = self.api_client.get('/_main/api/v1/asset/',
                                       format='json')
        self.assertValidJSONResponse(response)

        json = self.deserialize(response)
        objects = json['objects']
        self.assertEquals(len(objects), 4)

        self.assertAssetEquals(objects[0], 'Mediathread: Introduction',
                               'Instructor One', 'youtube', [2, 3, 17, 19],
                               'http://localhost:8002/site_media/img/test/'
                               'mediathread_introduction_thumb.jpg')

        self.assertAssetEquals(
            objects[1], 'MAAP Award Reception',
            'Instructor One', 'image', [5, 8, 10],
            'http://localhost:8002/site_media/img/test/maap_thumb.jpg')

        self.assertAssetEquals(
            objects[2],
            'The Armory - Home to CCNMTL\'S CUMC Office',
            'Instructor One', 'image', [7],
            'http://localhost:8002/site_media/img/test/armory_thumb.jpg')

        self.assertAssetEquals(
            objects[3],
            'Project Portfolio',
            'test_instructor_two', 'image', [],
            None)

    def test_student_getlist_restricted(self):
        # Set course details to restricted
        sample_course = Course.objects.get(title="Sample Course")
        sample_course.add_detail(course_details.SELECTION_VISIBILITY_KEY, 0)

        self.assertTrue(
            self.api_client.client.login(username="test_student_one",
                                         password="test"))

        response = self.api_client.get('/_main/api/v1/asset/',
                                       format='json')
        self.assertValidJSONResponse(response)

        json = self.deserialize(response)
        objects = json['objects']
        self.assertEquals(len(objects), 4)

        self.assertAssetEquals(objects[0], 'Mediathread: Introduction',
                               'Instructor One', 'youtube', [2, 3, 17, 19],
                               'http://localhost:8002/site_media/img/test/'
                               'mediathread_introduction_thumb.jpg')

        self.assertAssetEquals(
            objects[1], 'MAAP Award Reception',
            'Instructor One', 'image', [5, 8],
            'http://localhost:8002/site_media/img/test/maap_thumb.jpg')

        self.assertAssetEquals(
            objects[2],
            'The Armory - Home to CCNMTL\'S CUMC Office',
            'Instructor One', 'image', [7],
            'http://localhost:8002/site_media/img/test/armory_thumb.jpg')

        self.assertAssetEquals(
            objects[3],
            'Project Portfolio',
            'test_instructor_two', 'image', [],
            None)

    def test_student_getobject(self):
        self.assertTrue(
            self.api_client.client.login(username="test_student_one",
                                         password="test"))

        response = self.api_client.get('/_main/api/v1/asset/2/',
                                       format='json')
        self.assertValidJSONResponse(response)
        json = self.deserialize(response)

        self.assertAssetEquals(
            json, 'MAAP Award Reception',
            'Instructor One', 'image', [5, 8, 10],
            'http://localhost:8002/site_media/img/test/maap_thumb.jpg')

    def test_student_getobject_restricted(self):
        # Set course details to restricted
        sample_course = Course.objects.get(title="Sample Course")
        sample_course.add_detail(course_details.SELECTION_VISIBILITY_KEY, 0)

        self.assertTrue(
            self.api_client.client.login(username="test_student_one",
                                         password="test"))

        response = self.api_client.get('/_main/api/v1/asset/2/',
                                       format='json')
        self.assertValidJSONResponse(response)
        json = self.deserialize(response)

        self.assertAssetEquals(
            json, 'MAAP Award Reception',
            'Instructor One', 'image', [5, 8],
            'http://localhost:8002/site_media/img/test/maap_thumb.jpg')

    def test_instructor_getlist(self):
        self.assertTrue(
            self.api_client.client.login(username="test_instructor",
                                         password="test"))

        response = self.api_client.get('/_main/api/v1/asset/',
                                       format='json')
        self.assertValidJSONResponse(response)

        json = self.deserialize(response)
        objects = json['objects']
        self.assertEquals(len(objects), 4)

        self.assertAssetEquals(objects[0], 'Mediathread: Introduction',
                               'Instructor One', 'youtube', [2, 3, 17, 19],
                               'http://localhost:8002/site_media/img/test/'
                               'mediathread_introduction_thumb.jpg')

        self.assertAssetEquals(
            objects[1], 'MAAP Award Reception',
            'Instructor One', 'image', [5, 8, 10],
            'http://localhost:8002/site_media/img/test/maap_thumb.jpg')

        self.assertAssetEquals(
            objects[2],
            'The Armory - Home to CCNMTL\'S CUMC Office',
            'Instructor One', 'image', [7],
            'http://localhost:8002/site_media/img/test/armory_thumb.jpg')

        self.assertAssetEquals(
            objects[3],
            'Project Portfolio',
            'test_instructor_two', 'image', [],
            None)

    def test_instructor_getlist_restricted(self):
        # Set course details to restricted
        sample_course = Course.objects.get(title="Sample Course")
        sample_course.add_detail(course_details.SELECTION_VISIBILITY_KEY, 0)

        self.test_instructor_getlist()

    def test_instructor_getobject(self):
        self.assertTrue(
            self.api_client.client.login(username="test_instructor",
                                         password="test"))

        response = self.api_client.get('/_main/api/v1/asset/1/',
                                       format='json')
        self.assertValidJSONResponse(response)
        json = self.deserialize(response)

        self.assertAssetEquals(json, 'Mediathread: Introduction',
                               'Instructor One', 'youtube', [2, 3, 17, 19],
                               'http://localhost:8002/site_media/img/test/'
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
        response = self.api_client.get('/_main/api/v1/asset/1/',
                                       format='json')
        self.assertEqual(response.status_code, 404)

    def test_post_list(self):
        self.assertTrue(
            self.api_client.client.login(username="test_instructor",
                                         password="test"))

        self.assertHttpMethodNotAllowed(self.api_client.post(
            '/_main/api/v1/asset/', format='json', data={}))

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

    def test_getobject_multiple_class_member(self):
        self.assertTrue(
            self.api_client.client.login(username="test_student_three",
                                         password="test"))

        # Student One Selection from Sample Course
        response = self.api_client.get('/_main/api/v1/asset/1/',
                                       format='json')
        self.assertHttpOK(response)
        self.assertEquals(response.template[0].name,
                          "courseaffils/select_course.html")

        # No dice, login to Alternate Course
        response = self.api_client.client.get(
            '/?set_course=Alternate%20Course%20Members&next=/', follow=True)
        self.assertHttpOK(response)
        self.assertEquals(response.template[0].name, "homepage.html")

        # Let's try this again -- Student One Selection from Sample Course
        response = self.api_client.get('/_main/api/v1/asset/1/',
                                       format='json')
        self.assertValidJSONResponse(response)
        json = self.deserialize(response)
        self.assertAssetEquals(json, 'Mediathread: Introduction',
                               'Instructor One', 'youtube', [2, 3, 17, 19],
                               'http://localhost:8002/site_media/img/test/'
                               'mediathread_introduction_thumb.jpg')

        # Now ask for one from Alternate Course
        response = self.api_client.get('/_main/api/v1/asset/4/',
                                       format='json')
        self.assertValidJSONResponse(response)
        json = self.deserialize(response)
        self.assertAssetEquals(json, 'Design Research',
                               'test_instructor_alt', 'image',
                               [13, 14, 15],
                               None)

    def test_getlist_multiple_class_member(self):
        self.assertTrue(
            self.api_client.client.login(username="test_student_three",
                                         password="test"))

        # Student One Selection from Sample Course
        response = self.api_client.get('/_main/api/v1/asset/',
                                       format='json')
        self.assertHttpOK(response)
        self.assertEquals(response.template[0].name,
                          "courseaffils/select_course.html")

        # No dice, login to Alternate Course
        response = self.api_client.client.get(
            '/?set_course=Alternate%20Course%20Members&next=/', follow=True)
        self.assertHttpOK(response)
        self.assertEquals(response.template[0].name, "homepage.html")

        # Let's try this again -- asset list
        response = self.api_client.get('/_main/api/v1/asset/',
                                       format='json')

        json = self.deserialize(response)
        objects = json['objects']
        self.assertEquals(len(objects), 5)

        self.assertAssetEquals(objects[0], 'Mediathread: Introduction',
                               'Instructor One', 'youtube', [2, 3, 17, 19],
                               'http://localhost:8002/site_media/img/test/'
                               'mediathread_introduction_thumb.jpg')

        self.assertAssetEquals(
            objects[1], 'MAAP Award Reception',
            'Instructor One', 'image', [5, 8, 10],
            'http://localhost:8002/site_media/img/test/maap_thumb.jpg')

        self.assertAssetEquals(
            objects[2],
            'The Armory - Home to CCNMTL\'S CUMC Office',
            'Instructor One', 'image', [7],
            'http://localhost:8002/site_media/img/test/armory_thumb.jpg')

        self.assertAssetEquals(objects[3], 'Design Research',
                               'test_instructor_alt', 'image',
                               [13, 14, 15], None)

        self.assertAssetEquals(objects[4], 'Project Portfolio',
                               'test_instructor_two', 'image', [], None)

    def test_student_getlist_filtered(self):
        self.assertTrue(
            self.api_client.client.login(username="test_student_one",
                                         password="test"))

        # Get all assets w/notes by student two
        response = self.api_client.get(
            '/_main/api/v1/asset/?sherdnote_set__author__id=4',
            format='json')
        self.assertValidJSONResponse(response)

        json = self.deserialize(response)
        objects = json['objects']
        self.assertEquals(len(objects), 1)

        self.assertAssetEquals(
            objects[0], 'MAAP Award Reception',
            'Instructor One', 'image', [10],
            'http://localhost:8002/site_media/img/test/maap_thumb.jpg')

#     def test_student_getlist_bymodified(self):
#         self.assertTrue(
#             self.api_client.client.login(username="test_student_one",
#                                          password="test"))
#
#         user = User.objects.get(username="test_student_one")
#         asset = Asset.objects.get(id=1)
#         ga = asset.global_annotation(user, False)
#         ga.modified = datetime.today()
#         ga.save()
#
#         response = self.api_client.get('/_main/api/v1/asset/?modified=today',
#                                        format='json')
#         self.assertValidJSONResponse(response)
#
#         json = self.deserialize(response)
#         objects = json['objects']
#         self.assertEquals(len(objects), 4)
#
#         self.assertAssetEquals(objects[0], 'Mediathread: Introduction',
#                                'Instructor One', 'youtube', [2, 3, 17, 19],
#                                'http://localhost:8002/site_media/img/test/'
#                                'mediathread_introduction_thumb.jpg')
