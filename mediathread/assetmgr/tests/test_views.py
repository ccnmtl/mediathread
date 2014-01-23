#pylint: disable-msg=R0904
from django.conf import settings
from django.contrib.auth.models import User
from django.test import TestCase
from mediathread.assetmgr.models import Asset
from mediathread.djangosherd.models import SherdNote
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

    def test_annotation_save(self):
        asset = Asset.objects.get(id=2)

        # Update as the asset's non-original author. This should fail
        username = "test_student_one"
        self.assert_(self.client.login(username=username, password="test"))
        post_data = {'asset-title': "My MAAP Award Reception"}
        gann = SherdNote.objects.get(id=9)  # student one global ann
        url = "/asset/save/%s/annotations/%s/" % (asset.id, gann.id)
        response = self.client.post(url,
                                    post_data,
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEquals(response.status_code, 200)
        asset = Asset.objects.get(id=2)
        self.assertEquals(asset.title, "MAAP Award Reception")

        # Switch to the asset's original author
        username = "test_instructor"
        self.client.logout()
        self.assert_(self.client.login(username=username, password="test"))

        # Update as the asset's original author, this should succeed
        gann = SherdNote.objects.get(id=4)
        url = "/asset/save/%s/annotations/%s/" % (asset.id, gann.id)
        post_data = {'asset-title': "Updated MAAP Award Reception"}
        response = self.client.post(url,
                                    post_data,
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEquals(response.status_code, 200)
        asset = Asset.objects.get(id=2)
        self.assertEquals(asset.title, "Updated MAAP Award Reception")

        # Update passing in a non-global annotation. This should fail
        ann = SherdNote.objects.get(id=5)
        url = "/asset/save/%s/annotations/%s/" % (asset.id, ann.id)
        post_data = {'asset-title': "The New and Improved MAAP",
                     'annotation-range1': -4.5,
                     'annotation-range2': 23.0}
        response = self.client.post(url,
                                    post_data,
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEquals(response.status_code, 200)
        asset = Asset.objects.get(id=2)
        self.assertEquals(asset.title, "Updated MAAP Award Reception")

        # Test "no annotation" exception path
        url = "/asset/save/%s/annotations/%s/" % (asset.id, 42)
        post_data = {'asset-title': "The New and Improved Armory"}
        response = self.client.post(url,
                                    post_data,
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEquals(response.status_code, 403)

        # The remainder of the annotation update is tested in djangosherd

    def test_student_get_my_assets(self):
        username = "test_student_one"
        password = "test"
        self.assert_(self.client.login(username=username, password=password))

        response = self.client.get(
            "/asset/json/user/test_student_one/?annotations=true",
            {},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        json = simplejson.loads(response.content)

        self.assertTrue(json['editable'])
        self.assertFalse(json['citable'])
        self.assertFalse(json['is_faculty'])
        self.assertEquals(len(json['assets']), 1)
        self.assertEquals(len(json['assets'][0]['annotations']), 1)

    def test_student_get_peer_assets(self):
        username = "test_student_one"
        password = "test"
        self.assert_(self.client.login(username=username, password=password))

        record_owner = 'test_student_two'
        response = self.client.get(
            "/asset/json/user/%s/?annotations=true" % record_owner,
            {},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        json = simplejson.loads(response.content)

        self.assertFalse(json['editable'])
        self.assertFalse(json['citable'])
        self.assertFalse(json['is_faculty'])
        self.assertEquals(len(json['assets']), 1)
        self.assertEquals(len(json['assets'][0]['annotations']), 1)

        ann = json['assets'][0]['annotations'][0]
        self.assertEquals(len(ann['metadata']['tags']), 1)
        self.assertEquals(ann['metadata']['body'],
                          "student two selection note")

        self.assertTrue('global_annotation' in json['assets'][0])
        gla = json['assets'][0]['global_annotation']
        self.assertEquals(len(gla['metadata']['tags']), 1)
        self.assertEquals(gla['metadata']['body'],
                          "student two item note")

# Commented
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

    def test_save_server2server(self):
        setattr(settings,
                'SERVER_ADMIN_SECRETKEYS', {'http://localhost': 'testing'})

        post_data = {'set_course': "Sample_Course_Students",
                     'secret': 'testing',
                     'as': 'test_student_one',
                     'title': "Test Video",
                     "metadata-creator": "test_student_one",
                     "metadata-description": "a description",
                     "metadata-subject": "a subject",
                     "metadata-license": "video.license",
                     "metadata-language": "english",
                     "metadata-uuid": "26d62ca0-844f-11e3-a7ed-0002a5d5c51b",
                     "metadata-wardenclyffe-id": str(1234),
                     "metadata-tag": "upload",
                     "mp4-metadata": "w%dh%d" % (256, 256),
                     "mp4_pseudo": "http://stream.ccnmtl.columbia.edu/"
                     "secvideos/SECURE/d75ebcfa-8444-11e3-a075-00163e3b1544-"
                     "No_training_wheels-mp4-aac-480w-850kbps-ffmpeg.mp4"}

        response = self.client.post("/save/", post_data, follow=True)
        asset = Asset.objects.get(title="Test Video")
        self.assertRedirects(response,
                             "http://testserver/accounts/login/?next=/asset/" +
                             str(asset.id) + "/",
                             status_code=302,
                             target_status_code=200)
        self.assertEquals(asset.author.username, "test_student_one")
        self.assertEquals(asset.course.title, "Sample Course")
        user = User.objects.get(username='test_student_one')
        self.assertIsNotNone(asset.global_annotation(user, auto_create=False))

        # Repeat the post with a different user, verify there's no duplication
        post_data['as'] = 'test_instructor'
        response = self.client.post("/save/", post_data, follow=True)

        # There should only be one asset. This will raise if there are multiple
        asset = Asset.objects.get(title="Test Video")
        user = User.objects.get(username="test_instructor")
        self.assertIsNotNone(asset.global_annotation(user, auto_create=False))
