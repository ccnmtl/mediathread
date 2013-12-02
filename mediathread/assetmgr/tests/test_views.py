#pylint: disable-msg=R0904
from django.test import TestCase
import simplejson


class AssetViewTest(TestCase):
    fixtures = ['unittest_sample_course.json']

    def test_asset_detail(self):
        self.assertTrue(
            self.client.login(username='test_instructor_two', password='test'))

        response = self.client.get('/?set_course=Sample_Course_Students')
        self.assertEquals(response.status_code, 200)

        # Sample Course Asset
        response = self.client.get('/asset/1/',
                                   {},
                                   HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        json = simplejson.loads(response.content)
        self.assertEquals(json["asset_id"], "1")
        self.assertIsNone(json["annotation_id"])
        self.assertEquals(json["space_owner"], "test_instructor_two")
        self.assertEquals(len(json["panels"]), 1)

        panel = json["panels"][0]
        self.assertIsNone(panel["current_annotation"])
        self.assertEquals(panel["current_asset"], "1")
        self.assertEquals(panel["panel_state"], "open")
        self.assertEquals(panel["panel_state_label"], "Annotate Media")
        self.assertTrue(panel["show_collection"])
        self.assertEquals(panel["template"], "asset_workspace")
        self.assertTrue(panel["update_history"])
        self.assertEquals(len(panel["owners"]), 6)

        context = panel["context"]
        self.assertEquals(context["type"], "asset")
        self.assertTrue(context["user_settings"]["help_item_detail_view"])
        self.assertEquals(context["assets"]["1"]["annotation_count"], 0)

    def test_asset_detail_alternate(self):
        self.assertTrue(
            self.client.login(username='test_instructor_two', password='test'))

        response = self.client.get('/?set_course=Sample_Course_Students')
        self.assertEquals(response.status_code, 200)

        # Alternate Course Asset
        response = self.client.get('/asset/4/')
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed("asset_not_found.html")
        self.assertContains(response, "Oops!")
        self.assertContains(response, "Sample Course")
        self.assertContains(response, "Alternate Course")

    def test_asset_detail_does_not_exist(self):
        self.assertTrue(
            self.client.login(username='test_instructor_two', password='test'))

        response = self.client.get('/?set_course=Sample_Course_Students')
        self.assertEquals(response.status_code, 200)

        # Item Does Not Exist
        response = self.client.get('/asset/56/')
        self.assertEquals(response.status_code, 404)

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
