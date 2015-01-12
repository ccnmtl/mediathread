# pylint: disable-msg=R0904
import json

from django.test import TestCase
from django.test.client import RequestFactory

from mediathread.assetmgr.models import Asset
from mediathread.assetmgr.views import asset_workspace_courselookup, \
    asset_create, sources_from_args
from mediathread.djangosherd.models import SherdNote
from mediathread.factories import MediathreadTestMixin, AssetFactory, \
    SherdNoteFactory, UserFactory


class AssetViewTest(MediathreadTestMixin, TestCase):

    def setUp(self):
        self.setup_sample_course()
        self.setup_alternate_course()

        # instructor that sees both Sample Course & Alternate Course
        self.instructor_three = UserFactory(username='instructor_three')
        self.add_as_faculty(self.sample_course, self.instructor_three)
        self.add_as_faculty(self.alt_course, self.instructor_three)

    def test_sources_from_args(self):
        data = {'title': 'Bad Asset',
                'asset-source': 'bookmarklet',
                'image': "x" * 5000,  # too long
                'url': 'http://www.youtube.com/abcdefghi'}
        request = RequestFactory().post('/save/', data)
        sources = sources_from_args(request)

        self.assertEquals(len(sources.keys()), 0)

        data = {'title': 'Good Asset',
                'asset-source': 'bookmarklet',
                'image': "http://www.flickr.com/"}
        request = RequestFactory().post('/save/', data)
        sources = sources_from_args(request)
        self.assertEquals(len(sources.keys()), 2)
        self.assertEquals(sources['image'].url, "http://www.flickr.com/")
        self.assertTrue(sources['image'].primary)

    def test_archive_add_or_remove_get(self):
        self.assertTrue(
            self.client.login(username=self.instructor_one.username,
                              password='test'))

        response = self.client.get('/asset/archive/')
        self.assertEquals(response.status_code, 405)

    def test_archive_add_or_remove_notloggedin(self):
        response = self.client.post('/asset/archive/')
        self.assertEquals(response.status_code, 302)

    def test_archive_remove(self):
        archive = AssetFactory.create(course=self.sample_course,
                                      author=self.instructor_one,
                                      primary_source='archive')

        self.assertTrue(
            self.client.login(username=self.instructor_one.username,
                              password='test'))
        response = self.client.post('/asset/archive/',
                                    {'remove': True,
                                     'title': archive.title})
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
            self.client.login(username=self.instructor_one.username,
                              password='test'))
        self.client.post('/asset/archive/', data)

        self.assertIsNotNone(Asset.objects.get(course=self.sample_course,
                                               title='YouTube'))

    def test_asset_create_noasset(self):
        data = {'title': 'Bad Asset',
                'foobar': 'http://www.youtube.com/abcdefghi'}

        request = RequestFactory().post('/save/', data)
        request.user = self.instructor_one
        request.course = self.sample_course

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
        request.user = self.instructor_one
        request.course = self.sample_course

        response = asset_create(request)
        self.assertEquals(response.status_code, 200)

        Asset.objects.get(title='YouTube Asset')

    def test_asset_workspace_course_lookup(self):
        self.assertIsNone(asset_workspace_courselookup())

        asset1 = AssetFactory.create(course=self.sample_course,
                                     primary_source='image')

        self.assertEquals(asset_workspace_courselookup(asset_id=asset1.id),
                          asset1.course)

    def test_most_recent(self):
        self.assertTrue(
            self.client.login(username=self.instructor_one.username,
                              password='test'))

        asset1 = AssetFactory.create(course=self.sample_course,
                                     primary_source='image',
                                     author=self.instructor_one)

        response = self.client.get('/asset/most_recent/', {}, follow=True)
        self.assertEquals(response.status_code, 200)

        url = 'http://testserver/asset/%s/' % asset1.id
        self.assertEquals(response.redirect_chain, [(url, 302)])

    def test_asset_delete(self):
        self.assertTrue(
            self.client.login(username=self.instructor_one.username,
                              password='test'))

        asset1 = AssetFactory.create(course=self.sample_course,
                                     author=self.instructor_one,
                                     primary_source='image')
        self.student_note = SherdNoteFactory(
            asset=asset1, author=self.student_one)
        self.instructor_note = SherdNoteFactory(
            asset=asset1, author=self.instructor_one)

        response = self.client.get('/asset/delete/%s/' % asset1.id, {},
                                   HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEquals(response.status_code, 200)

        notes = asset1.sherdnote_set.filter(author=self.instructor_one)
        self.assertEquals(notes.count(), 0)
        notes = asset1.sherdnote_set.filter(author=self.student_one)
        self.assertEquals(notes.count(), 1)

    def test_asset_detail(self):
        self.assertTrue(
            self.client.login(username=self.instructor_one.username,
                              password='test'))

        asset1 = AssetFactory.create(course=self.sample_course,
                                     author=self.instructor_one,
                                     primary_source='image')

        response = self.client.get('/asset/%s/' % asset1.id, {},
                                   HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        the_json = json.loads(response.content)
        self.assertTrue("space_owner" not in the_json)
        self.assertEquals(len(the_json["panels"]), 1)

        panel = the_json["panels"][0]
        self.assertIsNone(panel["current_annotation"])
        self.assertEquals(panel["current_asset"], str(asset1.id))
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
            self.client.login(username=self.instructor_three.username,
                              password='test'))

        response = self.switch_course(self.client, self.sample_course)
        self.assertEquals(response.status_code, 200)

        asset1 = AssetFactory.create(course=self.alt_course,
                                     author=self.alt_instructor,
                                     primary_source='image')

        # Alternate Course Asset
        response = self.client.get('/asset/%s/' % asset1.id)
        self.assertEquals(response.status_code, 200)

        self.assertTemplateUsed(response, "assetmgr/asset_not_found.html")
        self.assertContains(response, "Oops!")
        self.assertContains(response, "Sample Course")
        self.assertContains(response, "Alternate Course")

    def test_asset_detail_does_not_exist(self):
        self.assertTrue(
            self.client.login(username=self.instructor_one.username,
                              password='test'))

        # Item Does Not Exist
        response = self.client.get('/asset/5616/')
        self.assertEquals(response.status_code, 404)

    def test_asset_title_save_as_non_author(self):
        asset1 = AssetFactory.create(course=self.sample_course,
                                     primary_source='image',
                                     title="Item Title")

        student_ga = SherdNoteFactory(
            asset=asset1, author=self.student_one,
            title=None, range1=None, range2=None)

        # Update as the asset's non-original author with ga. This should fail
        self.assert_(self.client.login(username=self.student_one.username,
                                       password="test"))
        post_data = {'asset-title': "Student Item"}
        url = "/asset/save/%s/annotations/%s/" % (asset1.id, student_ga.id)
        response = self.client.post(url, post_data,
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEquals(response.status_code, 200)
        updated_asset = Asset.objects.get(id=asset1.id)
        self.assertEquals(updated_asset.title, "Item Title")

    def test_asset_title_save_as_author_not_global_annotation(self):
        asset1 = AssetFactory.create(course=self.sample_course,
                                     primary_source='image',
                                     title="Item Title")

        note = SherdNoteFactory(
            asset=asset1, author=self.instructor_one)

        self.assert_(self.client.login(username=self.instructor_one.username,
                                       password="test"))

        # Update passing in a non-global annotation. This should fail
        post_data = {'asset-title': 'Updated Title',
                     'annotation-range1': -4.5, 'annotation-range2': 23.0}
        url = "/asset/save/%s/annotations/%s/" % (asset1.id, note.id)
        response = self.client.post(url, post_data,
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEquals(response.status_code, 200)
        asset = Asset.objects.get(id=asset1.id)
        self.assertEquals(asset.title, "Item Title")

    def test_asset_title_save_as_author_global_annotation(self):
        asset1 = AssetFactory.create(course=self.sample_course,
                                     primary_source='image',
                                     title="Item Title",
                                     author=self.instructor_one)

        gann = SherdNoteFactory(
            asset=asset1, author=self.instructor_one,
            title=None, range1=None, range2=None)

        self.assert_(self.client.login(username=self.instructor_one.username,
                                       password="test"))

        # Update passing in a non-global annotation. This should fail
        post_data = {'asset-title': "Updated Item Title"}
        url = "/asset/save/%s/annotations/%s/" % (asset1.id, gann.id)
        response = self.client.post(url, post_data,
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEquals(response.status_code, 200)
        asset = Asset.objects.get(id=asset1.id)
        self.assertEquals(asset.title, "Updated Item Title")

    def test_annotation_save(self):
        asset1 = AssetFactory.create(course=self.sample_course,
                                     primary_source='image',
                                     title="Item Title")

        note = SherdNoteFactory(
            asset=asset1, author=self.instructor_one)

        self.assert_(self.client.login(username=self.instructor_one.username,
                                       password="test"))

        # Update passing in a non-global annotation. This should fail
        url = "/asset/save/%s/annotations/%s/" % (asset1.id, note.id)
        post_data = {'annotation-range1': -4.5, 'annotation-range2': 23.0}
        response = self.client.post(url, post_data,
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEquals(response.status_code, 200)

        updated_note = SherdNote.objects.get(id=note.id)
        self.assertEquals(updated_note.range1, -4.5)
        self.assertEquals(updated_note.range2, 23.0)

    def test_annotation_save_no_annotation_exists(self):
        asset1 = AssetFactory.create(course=self.sample_course,
                                     primary_source='image',
                                     title="Item Title")

        self.assert_(self.client.login(username=self.instructor_one.username,
                                       password="test"))

        url = "/asset/save/%s/annotations/%s/" % (asset1.id, 42)
        post_data = {'annotation-range1': -4.5}
        response = self.client.post(url, post_data,
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEquals(response.status_code, 403)

    def test_save_server2server(self):
        secrets = {'http://testserver/': 'testing'}
        with self.settings(SERVER_ADMIN_SECRETKEYS=secrets):
            post_data = {'set_course': self.sample_course.group.name,
                         'secret': 'testing',
                         'as': self.student_one.username,
                         'title': "Test Video",
                         "metadata-creator": self.student_one.username,
                         "metadata-description": "a description",
                         "metadata-subject": "a subject",
                         "metadata-license": "video.license",
                         "metadata-language": "english",
                         "metadata-uuid": "26d62ca0-844f",
                         "metadata-wardenclyffe-id": str(1234),
                         "metadata-tag": "upload",
                         "mp4-metadata": "w%dh%d" % (256, 256),
                         "mp4_pseudo": "http://stream.ccnmtl.columbia.edu/"
                         "secvideos/SECURE/d75ebcfa-8444"
                         "No_training_wheels-mp4-aac-480w-850kbps-ffmpeg.mp4"}

            response = self.client.post("/save/", post_data, follow=True)
            asset = Asset.objects.get(title="Test Video")
            self.assertRedirects(
                response,
                "http://testserver/accounts/login/?next=/asset/%s/" % asset.id,
                status_code=302,
                target_status_code=200)
            self.assertEquals(asset.author.username, self.student_one.username)
            self.assertEquals(asset.course.title, "Sample Course")
            self.assertIsNotNone(asset.global_annotation(self.student_one,
                                                         auto_create=False))

            # Repeat the post with a different user, no duplication expected
            post_data['as'] = self.instructor_one
            response = self.client.post("/save/", post_data, follow=True)

            # There should only be one asset.
            asset = Asset.objects.get(title="Test Video")
            self.assertIsNotNone(asset.global_annotation(self.instructor_one,
                                                         auto_create=False))
