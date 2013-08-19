from django.test import TestCase
import simplejson


class AssetViewTest(TestCase):
    fixtures = ['unittest_sample_course.json']

    def test_student_get_my_assets(self):
        username = "test_student_one"
        password = "test"
        self.assert_(self.client.login(username=username, password=password))

        response = self.client.get(
            """/asset/json/user/test_student_one/?annotations=true""",
            {},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        json = simplejson.loads(response.content)

        self.assertTrue(json['editable'])
        self.assertFalse(json['citable'])
        self.assertFalse(json['is_faculty'])
        self.assertEquals(len(json['assets']), 1)
        self.assertEquals(len(json['assets'][0]['annotations']), 1)


#     def test_student_get_peer_assets(self):
#         username = "test_student_one"
#         password = "test"
#         self.assert_(self.client.login(username=username, password=password))
#
#         record_owner = 'test_student_two'
#
#     def test_student_get_peer_assets_restricted(self):
#         username = "test_student_one"
#         password = "test"
#         self.assert_(self.client.login(username=username, password=password))
#
#         record_owner = 'test_student_two'
#
#     def test_student_get_instructor_assets(self):
#         username = "test_student_one"
#         password = "test"
#         self.assert_(self.client.login(username=username, password=password))
#
#         record_owner = 'test_instructor'
#
#     def test_student_get_all_assets(self):
#         username = "test_student_one"
#         password = "test"
#         self.assert_(self.client.login(username=username, password=password))
#
#        record_owner = ''
#
#     def test_instructor_get_my_assets(self):
#         username = "test_instructor"
#         password = "test"
#         self.assert_(self.client.login(username=username, password=password))
#
#         record_owner = 'test_instructor'
#
#     def test_instructor_get_student_assets(self):
#         username = "test_instructor"
#         password = "test"
#         self.assert_(self.client.login(username=username, password=password))
#
#         record_owner = 'test_student_one'
#
#     def test_instructor_get_student_assets_restricted(self):
#         return self.test_instructor_get_student_assets()
#
#     def test_instructor_get_assets_by_course(self):
#         username = "test_instructor"
#         password = "test"
#         self.assert_(self.client.login(username=username, password=password))
#
#         record_owner = ''
