#pylint: disable-msg=R0904
from courseaffils.models import Course
from django.conf import settings
from django.contrib.auth.models import User
from django.test import TestCase
from django.test.client import RequestFactory
from mediathread.assetmgr.models import Asset, Source
from mediathread.assetmgr.views import asset_workspace_courselookup, \
    asset_create
from mediathread.djangosherd.models import SherdNote
import json


class AssetViewTest(TestCase):
    fixtures = ['unittest_sample_course.json']

    def test_archive_add_or_remove_get(self):
        self.assertTrue(
            self.client.login(username='test_instructor', password='test'))

        response = self.client.get('/asset/archive/')
        self.assertEquals(response.status_code, 405)

    def test_archive_add_or_remove_notloggedin(self):
        response = self.client.post('/asset/archive/')
        self.assertEquals(response.status_code, 302)

    def test_archive_remove(self):
        user = User.objects.get(username='test_instructor')
        course = Course.objects.get(title='Sample Course')
        archive = Asset.objects.create(title="Sample Archive",
                                       course=course, author=user)
        primary = Source.objects.create(asset=archive, label='archive',
                                        primary=True,
                                        url="http://ccnmtl.columbia.edu")
        archive.source_set.add(primary)

        self.assertIsNotNone(Asset.objects.get(title="Sample Archive"))

        self.assertTrue(
            self.client.login(username='test_instructor', password='test'))
        response = self.client.post('/asset/archive/',
                                    {'remove': True,
                                     'title': 'Sample Archive'})
        self.assertEquals(response.status_code, 302)

        try:
            Asset.objects.get(title="Sample Archive")
            self.fail('Sample archive should have been deleted')
        except Asset.DoesNotExist:
            pass  # expected

    def test_archive_add(self):
        data = {
            'thumb': '/site_media/img/thumbs/youtube.png',
            'title': 'YouTube',
            'url': 'http://www.youtube.com/',
            'archive': 'http://www.youtube.com/'}

        self.assertTrue(
            self.client.login(username='test_instructor', password='test'))
        self.client.post('/asset/archive/', data)

        self.assertIsNotNone(Asset.objects.get(course__title='Sample Course',
                                               title='YouTube'))

    def test_asset_create_noasset(self):
        data = {'title': 'Bad Asset',
                'foobar': 'http://www.youtube.com/abcdefghi'}

        request = RequestFactory().post('/save/', data)
        request.user = User.objects.get(username='test_instructor')
        request.course = Course.objects.get(title='Sample Course')

        try:
            asset_create(request)
            self.fail("An assertion error should have been raised")
        except AssertionError:
            pass  # expected

    def test_asset_create_via_bookmarklet(self):
        data = {'title': 'YouTube Asset',
                'youtube': 'http://www.youtube.com/abcdefghi',
                'asset-source': 'bookmarklet'}

        request = RequestFactory().post('/save/', data)
        request.user = User.objects.get(username='test_instructor')
        request.course = Course.objects.get(title='Sample Course')

        response = asset_create(request)
        self.assertEquals(response.status_code, 200)

        Asset.objects.get(title='YouTube Asset')

    def test_asset_workspace_course_lookup(self):
        self.assertIsNone(asset_workspace_courselookup())

        asset = Asset.objects.get(title='MAAP Award Reception')
        self.assertEquals(asset_workspace_courselookup(asset_id=asset.id),
                          asset.course)

    def test_most_recent(self):
        self.assertTrue(
            self.client.login(username='test_instructor', password='test'))

        response = self.client.get('/asset/most_recent/', {}, follow=True)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.redirect_chain,
                          [('http://testserver/asset/3/', 302)])

    def test_asset_delete(self):
        self.assertTrue(
            self.client.login(username='test_instructor', password='test'))

        asset = Asset.objects.get(title='MAAP Award Reception')
        user = asset.author
        self.assertEquals(asset.sherdnote_set.filter(author=user).count(), 2)
        response = self.client.get('/asset/delete/%s/' % asset.id,
                                   {},
                                   HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEquals(response.status_code, 200)

        self.assertEquals(asset.sherdnote_set.filter(author=user).count(), 0)

    def test_asset_detail(self):
        self.assertTrue(
            self.client.login(username='test_instructor_two', password='test'))

        response = self.client.get('/?set_course=Sample_Course_Students')
        self.assertEquals(response.status_code, 200)

        response = self.client.get('/asset/1/',
                                   {},
                                   HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        the_json = json.loads(response.content)
        self.assertTrue("space_owner" not in the_json)
        self.assertEquals(len(the_json["panels"]), 1)

        panel = the_json["panels"][0]
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

    def test_asset_detail_alternate(self):
        self.assertTrue(
            self.client.login(username='test_instructor_two', password='test'))

        response = self.client.get('/?set_course=Sample_Course_Students')
        self.assertEquals(response.status_code, 200)

        # Alternate Course Asset
        response = self.client.get('/asset/4/')
        self.assertEquals(response.status_code, 200)

        self.assertTemplateUsed(response, "assetmgr/asset_not_found.html")
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
