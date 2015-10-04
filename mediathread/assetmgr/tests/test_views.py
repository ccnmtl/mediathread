# pylint: disable-msg=R0904
import json

from django.core.urlresolvers import reverse
from django.http.response import Http404, HttpResponseRedirect
from django.test import TestCase
from django.test.client import RequestFactory

from mediathread.assetmgr.models import Asset, ExternalCollection
from mediathread.assetmgr.views import asset_workspace_courselookup, \
    RedirectToExternalCollectionView, \
    RedirectToUploaderView, _parse_user, AssetCreateView
from mediathread.djangosherd.models import SherdNote
from mediathread.factories import MediathreadTestMixin, AssetFactory, \
    SherdNoteFactory, UserFactory, ExternalCollectionFactory, \
    SuggestedExternalCollectionFactory


class AssetViewTest(MediathreadTestMixin, TestCase):

    def setUp(self):
        self.setup_sample_course()
        self.setup_alternate_course()

        self.superuser = UserFactory(is_staff=True, is_superuser=True)

        # instructor that sees both Sample Course & Alternate Course
        self.instructor_three = UserFactory(username='instructor_three')
        self.add_as_faculty(self.sample_course, self.instructor_three)
        self.add_as_faculty(self.alt_course, self.instructor_three)

    def test_sources_from_args(self):
        data = {'title': 'Bad Asset',
                'asset-source': 'bookmarklet',
                'image': 'x' * 5000,  # too long
                'url': 'http://www.youtube.com/abcdefghi'}
        request = RequestFactory().post('/save/', data)
        sources = AssetCreateView.sources_from_args(request)

        self.assertEquals(len(sources.keys()), 0)

        data = {'title': 'Good Asset',
                'asset-source': 'bookmarklet',
                'image': 'http://www.flickr.com/',
                'image-metadata': [u'w720h526;text/html']}
        request = RequestFactory().post('/save/', data)
        sources = AssetCreateView.sources_from_args(request)
        self.assertEquals(len(sources.keys()), 2)
        self.assertEquals(sources['image'].url, 'http://www.flickr.com/')
        self.assertTrue(sources['image'].primary)
        self.assertEquals(sources['image'].width, 720)
        self.assertEquals(sources['image'].height, 526)
        self.assertEquals(sources['image'].media_type, 'text/html')

    def test_manage_external_collection_get(self):
        self.assertTrue(
            self.client.login(username=self.instructor_one.username,
                              password='test'))

        response = self.client.get('/asset/archive/')
        self.assertEquals(response.status_code, 405)

    def test_manage_external_collection_notloggedin(self):
        response = self.client.post('/asset/archive/')
        self.assertEquals(response.status_code, 302)

    def test_manage_external_collection_remove(self):
        exc = ExternalCollectionFactory(course=self.sample_course)

        self.assertTrue(
            self.client.login(username=self.instructor_one.username,
                              password='test'))
        response = self.client.post('/asset/archive/',
                                    {'remove': True,
                                     'collection_id': exc.id})
        self.assertEquals(response.status_code, 302)

        with self.assertRaises(Asset.DoesNotExist):
            Asset.objects.get(id=exc.id)

    def test_manage_external_collection_add_custom(self):
        data = {
            'title': 'YouTube',
            'url': 'http://www.youtube.com/',
            'thumb_url': '/site_media/img/thumbs/youtube.png',
            'description': 'http://www.youtube.com/'}

        self.assertTrue(
            self.client.login(username=self.instructor_one.username,
                              password='test'))
        self.client.post('/asset/archive/', data)

        ExternalCollection.objects.get(course=self.sample_course,
                                       title='YouTube')

    def test_manage_external_collection_add_suggested(self):
        suggested = SuggestedExternalCollectionFactory()
        data = {'suggested_id': suggested.id}

        self.assertTrue(
            self.client.login(username=self.instructor_one.username,
                              password='test'))
        self.client.post('/asset/archive/', data)

        ExternalCollection.objects.get(course=self.sample_course,
                                       title=suggested.title)

    def test_asset_create_noasset(self):
        data = {'title': 'Bad Asset',
                'foobar': 'http://www.youtube.com/abcdefghi'}

        request = RequestFactory().post('/save/', data)
        request.user = self.instructor_one
        request.course = self.sample_course

        with self.assertRaises(AssertionError):
            view = AssetCreateView()
            view.request = request
            view.post(request)

    def test_asset_create_via_bookmarklet(self):
        data = {'title': 'YouTube Asset',
                'youtube': 'http://www.youtube.com/abcdefghi',
                'asset-source': 'bookmarklet'}

        request = RequestFactory().post('/save/', data)
        request.user = self.instructor_one
        request.course = self.sample_course

        view = AssetCreateView()
        view.request = request
        response = view.post(request)

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

    def test_redirect_external_collection(self):
        view = RedirectToExternalCollectionView()
        request = RequestFactory().get(reverse('collection_redirect',
                                               args=[82]))

        with self.assertRaises(Http404):
            view.get(request, 456)

        exc = ExternalCollectionFactory(url='http://ccnmtl.columbia.edu')
        request = RequestFactory().get(reverse('collection_redirect',
                                               args=[exc.id]))
        response = view.get(request, exc.id)
        self.assertEquals(response.status_code, 302)
        self.assertEquals(response.url, 'http://ccnmtl.columbia.edu')

    def test_redirect_uploader(self):
        # no collection id
        request = RequestFactory().post('/upload/redirect')
        request.user = self.student_one
        request.course = self.sample_course

        view = RedirectToUploaderView()
        view.request = request

        with self.assertRaises(Http404):
            view.post(request, [], **{'collection_id': 123})

        secret_keys = {'http://ccnmtl.columbia.edu': 'a very good secret'}
        with self.settings(SERVER_ADMIN_SECRETKEYS=secret_keys):
            # invalid uploader url
            as_user = 'as=%s' % self.student_one.username
            exc = ExternalCollectionFactory(url='http://abc.def.ghi')
            with self.assertRaises(Http404):
                view.post(request, [], **{'collection_id': exc.id})

            # successful redirect
            exc = ExternalCollectionFactory(url='http://ccnmtl.columbia.edu')
            response = view.post(request, [], **{'collection_id': exc.id})
            self.assertEquals(response.status_code, 302)
            self.assertTrue(response.url.startswith(exc.url))
            self.assertTrue('nonce' in response.url)
            self.assertTrue('hmac' in response.url)
            self.assertTrue('redirect_url' in response.url)
            self.assertTrue(as_user in response.url)

            # "as" without permissions + audio
            data = {'as': self.student_two.username, 'audio': 'mp4'}
            request = RequestFactory().post('/upload/redirect', data)
            request.user = self.student_one
            request.course = self.sample_course
            response = view.post(request, [], **{'collection_id': exc.id})
            self.assertEquals(response.status_code, 302)
            self.assertTrue(as_user in response.url)
            self.assertTrue('audio=mp4' in response.url)

            # "as" with permissions
            data = {'as': self.student_one.username}
            request = RequestFactory().post('/upload/redirect', data)
            request.user = UserFactory(is_staff=True)
            request.course = self.sample_course
            self.add_as_faculty(request.course, request.user)

            response = view.post(request, [], **{'collection_id': exc.id})
            self.assertEquals(response.status_code, 302)
            self.assertTrue(as_user in response.url)

    def test_parse_user(self):
        request = RequestFactory().get('/')
        request.course = self.sample_course

        # regular path
        request.user = self.student_one
        self.assertEquals(_parse_user(request), self.student_one)

        # not a course member
        request.user = self.alt_student
        response = _parse_user(request)
        self.assertEquals(response.status_code, 403)

        # "as" without permissions
        request = RequestFactory().get('/', {'as': self.student_two.username})
        request.user = self.student_one
        request.course = self.sample_course
        self.assertEquals(_parse_user(request), self.student_one)

        # "as" with permissions
        request.user = UserFactory(is_staff=True)
        request.course = self.sample_course
        self.add_as_faculty(request.course, request.user)
        self.assertEquals(_parse_user(request), self.student_two)

    def test_scalar_no_super_redirect(self):
        request = RequestFactory().get('/')
        request.course = self.sample_course

        response = self.client.get("/asset/scalar/")
        self.assertTrue(isinstance(response, HttpResponseRedirect))

    def test_scalar_super_no_redirect(self):
        request = RequestFactory().get('/')
        request.course = self.sample_course
        self.client.login(username=self.superuser.username,
                          password='test')
        self.switch_course(self.client, self.sample_course)

        response = self.client.get("/asset/scalar/")
        self.assertFalse(isinstance(response, HttpResponseRedirect))
