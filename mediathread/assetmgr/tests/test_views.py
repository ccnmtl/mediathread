# pylint: disable-msg=R0904
from __future__ import unicode_literals

import datetime
import hashlib
import hmac
from json import loads
import json

from django.core.cache import cache
from django.urls import reverse
from django.http.response import Http404, HttpResponseRedirect
from django.test import TestCase
from django.test.client import RequestFactory

from mediathread.assetmgr.models import Asset, ExternalCollection
from mediathread.assetmgr.views import (
    EMBED_WIDTH, EMBED_HEIGHT,
    asset_workspace_courselookup,
    RedirectToExternalCollectionView,
    RedirectToUploaderView, AssetCreateView, AssetEmbedListView,
    _parse_domain, AssetEmbedView, annotation_delete,
    annotation_create_global, annotation_create, AssetUpdateView)
from mediathread.djangosherd.models import SherdNote
from mediathread.factories import MediathreadTestMixin, AssetFactory, \
    SherdNoteFactory, UserFactory, ExternalCollectionFactory, \
    SuggestedExternalCollectionFactory, SourceFactory
from mediathread.main.course_details import UPLOAD_FOLDER_KEY


class AssetViewTest(MediathreadTestMixin, TestCase):

    def setUp(self):
        self.setup_sample_course()
        self.setup_alternate_course()

        self.superuser = UserFactory(is_staff=True, is_superuser=True)

        # instructor that sees both Sample Course & Alternate Course
        self.instructor_three = UserFactory(username='instructor_three')
        self.add_as_faculty(self.sample_course, self.instructor_three)
        self.add_as_faculty(self.alt_course, self.instructor_three)

    def tearDown(self):
        cache.clear()

    def test_asset_access(self):
        item = AssetFactory.create(course=self.alt_course,
                                   primary_source='image')
        note = SherdNoteFactory(asset=item, author=self.alt_instructor,
                                title="Selection", range1=1, range2=2)

        item_url = reverse('asset-view', kwargs={'asset_id': item.id})
        note_url = reverse('annotation-view',
                           kwargs={'asset_id': item.id, 'annot_id': note.id})

        # sample course members can't see alt course assets
        self.client.login(username=self.student_one.username, password='test')
        self.assertEquals(self.client.get(item_url).status_code, 404)
        self.assertEquals(self.client.get(note_url).status_code, 404)

    def test_post_noasset(self):
        self.client.login(username=self.student_one.username, password='test')
        r = self.client.post(
            reverse('asset-save'), {
                'asset-source': 'bookmarklet',
                'title': 'Untitled',
                'url': 'http://stagely.artstor.org/library/#3|search|6'
                '|All20Collections3A20ruben|Filtered20Search|||type3D3'
                '626kw3Druben26geoIds3D26clsIds3D26collTypes3D26id3Dal'
                'l26bDate3D26eDate3D26dExact3D3126prGeoId3D26origKW3D'
            }, format='json')
        self.assertEqual(r.status_code, 400)
        self.assertEqual(
            r.content, b'The selected asset didn\'t have the '
            b'correct data to be imported into Mediathread.')

    def test_sources_from_args(self):
        data = {'title': 'Bad Asset',
                'asset-source': 'bookmarklet',
                'image': 'x' * 5000,  # too long
                'url': 'https://www.youtube.com/abcdefghi'}
        request = RequestFactory().post('/save/', data)
        sources = AssetCreateView.sources_from_args(request)

        self.assertEquals(len(sources.keys()), 0)

        data = {'title': 'Good Asset',
                'asset-source': 'bookmarklet',
                'image': 'https://www.flickr.com/',
                'image-metadata': ['w720h526;text/html']}
        request = RequestFactory().post('/save/', data)
        sources = AssetCreateView.sources_from_args(request)
        self.assertEquals(len(sources.keys()), 2)
        self.assertEquals(sources['image'].url, 'https://www.flickr.com/')
        self.assertTrue(sources['image'].primary)
        self.assertEquals(sources['image'].width, 720)
        self.assertEquals(sources['image'].height, 526)
        self.assertEquals(sources['image'].media_type, 'text/html')

        data = {
            'title': 'HTML5 video title',
            'asset-source': 'bookmarklet',
            'video': 'http://www.example.com/video.mp4',
            'video-metadata': 'w480h358',
            'metadata-description': 'Video description',
        }
        request = RequestFactory().post('/save/', data)
        sources = AssetCreateView.sources_from_args(request)
        self.assertEquals(len(sources.keys()), 2)
        self.assertEquals(sources['video'].url,
                          'http://www.example.com/video.mp4')
        self.assertTrue(sources['video'].primary)
        self.assertEquals(sources['video'].width, 480)
        self.assertEquals(sources['video'].height, 358)

    def test_parse_user(self):
        view = AssetCreateView()
        request = RequestFactory().get('/')
        request.course = self.sample_course

        # regular path
        request.user = self.student_one
        self.assertEquals(view.parse_user(request), self.student_one)

        # "as" without permissions
        request = RequestFactory().get('/', {'as': self.student_two.username})
        request.user = self.student_one
        request.course = self.sample_course
        self.assertEquals(view.parse_user(request), self.student_one)

        # "as" with permissions
        request.user = UserFactory(is_staff=True)
        request.course = self.sample_course
        self.add_as_faculty(request.course, request.user)
        self.assertEquals(view.parse_user(request), self.student_two)

    def test_manage_external_collection_get(self):
        self.assertTrue(
            self.client.login(username=self.instructor_one.username,
                              password='test'))
        self.switch_course(self.client, self.sample_course)

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
        self.switch_course(self.client, self.sample_course)
        response = self.client.post('/asset/archive/',
                                    {'remove': True,
                                     'collection_id': exc.id})
        self.assertEquals(response.status_code, 302)

        with self.assertRaises(Asset.DoesNotExist):
            Asset.objects.get(id=exc.id)

    def test_manage_external_collection_add_custom(self):
        data = {
            'title': 'YouTube',
            'url': 'https://www.youtube.com/',
            'thumb_url': '/site_media/img/thumbs/youtube.png',
            'description': 'https://www.youtube.com/'}

        self.assertTrue(
            self.client.login(username=self.instructor_one.username,
                              password='test'))
        self.switch_course(self.client, self.sample_course)
        self.client.post('/asset/archive/', data)

        ExternalCollection.objects.get(course=self.sample_course,
                                       title='YouTube')

    def test_manage_external_collection_add_suggested(self):
        suggested = SuggestedExternalCollectionFactory()
        data = {'suggested_id': suggested.id}

        self.assertTrue(
            self.client.login(username=self.instructor_one.username,
                              password='test'))
        self.switch_course(self.client, self.sample_course)
        self.client.post('/asset/archive/', data)

        ExternalCollection.objects.get(course=self.sample_course,
                                       title=suggested.title)

    def test_manage_ingest_get(self):
        self.assertTrue(
            self.client.login(username=self.instructor_one.username,
                              password='test'))
        self.switch_course(self.client, self.sample_course)

        response = self.client.get('/asset/ingest/')
        self.assertEquals(response.status_code, 405)

    def test_asset_create_via_bookmarklet(self):
        data = {'title': 'YouTube Asset',
                'youtube': 'https://www.youtube.com/abcdefghi',
                'asset-source': 'bookmarklet'}

        request = RequestFactory().post('/save/', data)
        request.user = self.instructor_one
        request.course = self.sample_course

        view = AssetCreateView()
        view.request = request
        response = view.post(request)

        self.assertEquals(response.status_code, 200)
        Asset.objects.get(title='YouTube Asset')

        data = {
            'title': 'HTML5 video title',
            'asset-source': 'bookmarklet',
            'video': 'http://www.example.com/video.mp4',
            'video-metadata': 'w480h358',
            'metadata-description': 'Video description',
        }
        request = RequestFactory().post('/save/', data)
        request.user = self.instructor_one
        request.course = self.sample_course

        view = AssetCreateView()
        view.request = request
        response = view.post(request)

        self.assertEquals(response.status_code, 200)
        asset = Asset.objects.get(title='HTML5 video title')
        self.assertEquals(asset.metadata()['description'],
                          [data['metadata-description']])

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
        self.switch_course(self.client, self.sample_course)
        asset1 = AssetFactory.create(course=self.sample_course,
                                     primary_source='image',
                                     author=self.instructor_one)

        response = self.client.get('/asset/most_recent/', {}, follow=True)
        self.assertEquals(response.status_code, 200)

        url = '/course/%s/react/asset/%s/' % \
            (self.sample_course.id, asset1.id)
        self.assertEquals(response.redirect_chain, [(url, 302)])

    def test_asset_delete(self):
        self.assertTrue(
            self.client.login(username=self.instructor_one.username,
                              password='test'))
        self.switch_course(self.client, self.sample_course)

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
        self.switch_course(self.client, self.sample_course)

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
        self.assertEquals(panel["current_asset"], asset1.id)
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
        self.switch_course(self.client, self.sample_course)

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
        self.switch_course(self.client, self.sample_course)

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
        self.switch_course(self.client, self.sample_course)

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
        self.switch_course(self.client, self.sample_course)

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
        self.switch_course(self.client, self.sample_course)

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
                "/accounts/login/?next=/asset/%s/" % asset.id,
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

    def test_redirect_uploader_get_folder(self):
        request = RequestFactory().post('/upload/redirect')
        request.user = self.student_one
        request.course = self.sample_course

        view = RedirectToUploaderView()
        view.request = request
        self.assertEquals(view.get_upload_folder(), '')

        self.sample_course.add_detail(UPLOAD_FOLDER_KEY, 'z')
        self.assertEquals(view.get_upload_folder(), 'z')

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

    def test_annotation_create(self):
        data = {'annotation-title': 'Annotation Test',
                'annotation-body': 'notes go here',
                'annotation-annotation_data': '',
                'annotation-range1': -4.5, 'annotation-range2': 23,
                'annotation-tags': 'foo,bar'}
        request = RequestFactory().post('/', data)
        request.user = self.student_one
        request.course = self.sample_course

        with self.assertRaises(Http404):
            annotation_create(request, 1234)

        asset = AssetFactory(course=self.sample_course, primary_source='image')
        response = annotation_create(request, asset.id)
        self.assertEquals(response.status_code, 302)

        note = SherdNote.objects.get(title='Annotation Test', asset=asset)
        self.assertEquals(note.range1, -4.5)
        self.assertEquals(note.range2, 23)
        self.assertEquals(note.tags, 'foo,bar')

    def test_annotation_create_global(self):
        asset = AssetFactory(course=self.sample_course, primary_source='image')
        request = RequestFactory().post('/', {},
                                        HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        request.user = self.student_one
        request.course = self.sample_course
        response = annotation_create_global(request, asset.id)
        self.assertEquals(response.status_code, 200)

        ga = asset.global_annotation(self.student_one, auto_create=False)
        self.assertIsNotNone(ga)

        the_json = loads(response.content)
        self.assertEquals(the_json['asset']['id'], asset.id)
        self.assertEquals(the_json['annotation']['id'], ga.id)

        # invalid asset
        with self.assertRaises(Http404):
            annotation_create_global(request, 1234)

    def test_annotation_delete(self):
        asset = AssetFactory(course=self.sample_course, primary_source='image')
        note = SherdNoteFactory(
            asset=asset, author=self.student_one,
            tags=',student_one_selection', range1=0, range2=1)

        request = RequestFactory().post('/')
        request.user = self.student_one
        request.course = self.sample_course

        response = annotation_delete(request, asset.id, note.id)
        self.assertEquals(response.status_code, 302)

        response = annotation_delete(request, asset.id, note.id)
        self.assertEquals(response.status_code, 404)

    def test_copy_annotation(self):
        asset = AssetFactory(course=self.sample_course, primary_source='image')

        self.assertIsNone(asset.global_annotation(self.student_two, False))

        note = SherdNoteFactory(
            asset=asset, author=self.student_one,
            title='Sample Note', annotation_data='{1:2}',
            body='student one notes',
            tags=',student_one_selection', range1=0, range2=1)

        params = {'asset_id': asset.id, 'annotation_id': note.id}

        url = reverse('annotation-copy-view', args=[asset.id, note.id])
        self.client.login(username=self.student_two.username,
                          password='test')
        response = self.client.post(url, params,
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        the_json = loads(response.content)

        self.assertEquals(the_json['asset']['id'], asset.id)
        self.assertNotEquals(the_json['annotation']['id'], note.id)

        self.assertEquals(response.status_code, 200)
        note = SherdNote.objects.get(author=self.student_two, title=note.title,
                                     range1=note.range1, range2=note.range2,
                                     annotation_data=note.annotation_data)
        self.assertEquals(note.tags, '')
        self.assertIsNone(note.body)
        self.assertIsNotNone(asset.global_annotation(self.student_two, False))


class AssetEmbedViewsTest(MediathreadTestMixin, TestCase):

    def setUp(self):
        self.setup_sample_course()
        self.url = reverse('asset-embed-list')

    def tearDown(self):
        cache.clear()

    def test_parse_domain(self):
        url = 'https://github.com/ccnmtl/mediathread/pull/354'
        self.assertEquals(_parse_domain(url), 'https://github.com/')

    def test_anonymous_user(self):
        # not logged in
        self.assertEquals(self.client.get(self.url).status_code, 302)

    def test_get(self):
        return_url = 'http://foo.bar/baz/'
        self.client.login(username=self.instructor_one.username,
                          password='test')
        self.switch_course(self.client, self.sample_course)
        response = self.client.get(self.url, {'return_url': return_url})
        self.assertEquals(response.status_code, 200)

        the_owners = loads(response.context_data['owners'])
        self.assertEquals(len(the_owners), 5)
        self.assertEquals(response.context_data['return_url'], return_url)

    def test_get_selection(self):
        asset = AssetFactory.create(course=self.sample_course,
                                    primary_source='image',
                                    author=self.instructor_one)
        gann = SherdNoteFactory(
            asset=asset, author=self.instructor_one,
            title=None, range1=None, range2=None)
        note = SherdNoteFactory(asset=asset, author=self.instructor_one,
                                title='Selection')

        view = AssetEmbedListView()

        keys = ['foo-1234']
        self.assertIsNone(view.get_selection(keys, self.instructor_one))

        with self.assertRaises(Http404):
            keys = ['item-666']
            view.get_selection(keys, self.instructor_one)

        with self.assertRaises(Http404):
            keys = ['selection-666']
            view.get_selection(keys, self.instructor_one)

        keys = ['item-%s' % asset.id]
        view = AssetEmbedListView()
        self.assertEquals(view.get_selection(keys, self.instructor_one), gann)

        keys = ['selection-%s' % note.id]
        view = AssetEmbedListView()
        self.assertEquals(view.get_selection(keys, self.instructor_one), note)

    def test_get_dimensions_image(self):
        asset = AssetFactory.create(course=self.sample_course,
                                    primary_source='image',
                                    author=self.instructor_one)
        primary = asset.primary

        view = AssetEmbedListView()
        dims = view.get_dimensions(primary)
        self.assertEquals(dims['width'], EMBED_WIDTH)
        self.assertEquals(dims['height'], EMBED_HEIGHT)

        # set a width/height
        primary.width = 400
        primary.height = 600
        primary.save()

        dims = view.get_dimensions(primary)
        self.assertEquals(dims['width'], EMBED_WIDTH)
        self.assertEquals(dims['height'], EMBED_HEIGHT)

    def test_get_dimensions_video(self):
        asset = AssetFactory.create(
            course=self.sample_course, primary_source='youtube')

        self.assertEquals(asset.media_type(), 'video')

        view = AssetEmbedListView()
        dims = view.get_dimensions(asset.primary)
        self.assertEquals(dims['width'], EMBED_WIDTH)
        self.assertEquals(dims['height'], EMBED_HEIGHT)

    def test_get_secret(self):
        secrets = {'http://testserver/': 'testing'}
        with self.settings(SERVER_ADMIN_SECRETKEYS=secrets):
            view = AssetEmbedListView()

            with self.assertRaises(Http404):
                view.get_secret('http://foo.bar')

            self.assertEquals(view.get_secret('http://testserver/a/b/c'),
                              'testing')

    def test_get_iframe_url(self):
        view = AssetEmbedListView()
        view.request = RequestFactory().get('/')
        view.request.course = self.sample_course

        asset = AssetFactory.create(course=self.sample_course,
                                    primary_source='image',
                                    author=self.instructor_one)
        note = SherdNoteFactory(asset=asset, author=self.instructor_one,
                                title='Selection')

        url = view.get_iframe_url('secret', note)
        x = 'http%3A%2F%2Ftestserver%2Fasset%2Fembed%2Fview%2F{}%2F{}%2F%3F'
        prefix = x.format(self.sample_course.id, note.id)
        self.assertTrue(url.startswith(prefix))
        self.assertTrue('nonce' in url)
        self.assertTrue('hmac' in url)

    def test_embed_view(self):
        asset = AssetFactory.create(course=self.sample_course,
                                    primary_source='image',
                                    author=self.instructor_one)
        note = SherdNoteFactory(asset=asset, author=self.instructor_one,
                                title='Selection')

        nonce = '%smthc' % datetime.datetime.now().isoformat()
        digest = hmac.new(
            'secret'.encode('utf-8'),
            '{}:{}:{}'.format(
                self.sample_course.id, note.id, nonce).encode('utf-8'),
            hashlib.sha1).hexdigest()

        view = AssetEmbedView()
        view.request = RequestFactory().get(
            '/', {'nonce': nonce, 'hmac': digest},
            HTTP_REFERER='http://testserver/a/b/c/')
        view.request.course = self.sample_course
        view.request.user = self.instructor_one

        with self.assertRaises(Http404):
            view.get_context_data(course_id=self.sample_course.id,
                                  annot_id=note.id)

        secrets = {'http://testserver/': 'secret'}
        with self.settings(SERVER_ADMIN_SECRETKEYS=secrets):
            ctx = view.get_context_data(course_id=self.sample_course.id,
                                        annot_id=note.id)

            self.assertTrue('item' in ctx)
            self.assertEquals(ctx['item_id'], asset.id)
            self.assertEquals(ctx['selection_id'], note.id)
            self.assertEquals(ctx['presentation'], 'medium')
            self.assertEquals(ctx['title'], 'Selection')


class AssetReferenceViewTest(MediathreadTestMixin, TestCase):

    def setUp(self):
        self.setup_sample_course()

    def tearDown(self):
        cache.clear()

    def test_get(self):
        asset = AssetFactory(course=self.sample_course, primary_source='image')
        SherdNoteFactory(
            asset=asset, author=self.student_one,
            tags=',student_one_selection', range1=0, range2=1)
        SherdNoteFactory(
            asset=asset, author=self.student_one,
            tags=',student_one_item', title=None, range1=None, range2=None)

        url = reverse('asset-references', args=[asset.id])

        # anonymous
        response = self.client.get(url)
        self.assertEquals(response.status_code, 302)

        self.client.login(username=self.student_one, password='test')

        # non-ajax
        response = self.client.get(url)
        self.assertEquals(response.status_code, 405)

        # ajax
        response = self.client.get(url, {},
                                   HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEquals(response.status_code, 200)
        the_json = loads(response.content)
        self.assertTrue('tags' in the_json)
        self.assertTrue('vocabulary' in the_json)
        self.assertTrue('references' in the_json)

        # invalid asset
        url = reverse('asset-references', args=[1234])
        response = self.client.get(url, {},
                                   HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEquals(response.status_code, 200)
        the_json = loads(response.content)
        self.assertFalse('tags' in the_json)
        self.assertFalse('vocabulary' in the_json)
        self.assertFalse('references' in the_json)


class BookmarkletMigrationViewTest(TestCase):

    def test_get(self):
        response = self.client.get(reverse('bookmarklet_migration'))
        self.assertEquals(response.status_code, 200)


class TagCollectionViewTest(MediathreadTestMixin, TestCase):

    def setUp(self):
        self.setup_sample_course()
        self.url = reverse('tag-collection-view')

    def tearDown(self):
        cache.clear()

    def test_get_anonymous(self):
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 302)

    def test_get_non_ajax(self):
        self.client.login(username=self.student_one.username, password='test')
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 405)

    def test_get(self):
        asset = AssetFactory(course=self.sample_course, primary_source='image')

        self.client.login(username=self.student_one.username, password='test')
        SherdNoteFactory(
            asset=asset, author=self.student_one,
            tags=',student_one_selection', range1=0, range2=1)
        SherdNoteFactory(
            asset=asset, author=self.student_one,
            tags=',student_one_item', title=None, range1=None, range2=None)

        response = self.client.get(self.url, {},
                                   HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEquals(response.status_code, 200)
        the_json = loads(response.content)
        self.assertTrue('tags' in the_json)
        self.assertEquals(len(the_json['tags']), 2)
        self.assertEquals(the_json['tags'][0]['name'], 'student_one_item')
        self.assertEquals(the_json['tags'][1]['name'], 'student_one_selection')


class AssetUpdateViewTest(MediathreadTestMixin, TestCase):

    def setUp(self):
        self.setup_sample_course()
        self.asset = AssetFactory(
            course=self.sample_course, primary_source='flv',
            metadata_blob='{"wardenclyffe-id": ["33210"], "license": [""]')
        SourceFactory(asset=self.asset, label='thumb', url='foo')

        self.url = reverse('asset-update-view')

        self.params = {
            'secret': 'something secret',
            'metadata-uuid': '1234567',
            'metadata-tag': 'update',
            'thumb': 'new thumb',
            'mp4_pseudo': ''
        }

    def test_get_matching_assets(self):
        self.assertEquals(
            AssetUpdateView().get_matching_assets('123').count(), 0)

        self.assertEquals(
            AssetUpdateView().get_matching_assets('33210').first(), self.asset)

    def test_not_allowed(self):
        # anonymous get or post
        response = self.client.get(self.url, self.params)
        self.assertEquals(response.status_code, 405)
        response = self.client.post(self.url, self.params)
        self.assertEquals(response.status_code, 403)

        # logged in get or post
        self.client.login(username=self.instructor_one.username,
                          password='test')
        self.switch_course(self.client, self.sample_course)

        response = self.client.get(self.url, self.params)
        self.assertEquals(response.status_code, 405)

        response = self.client.post(self.url, self.params)
        self.assertEquals(response.status_code, 403)

    def test_not_found(self):
        secrets = {'http://testserver/': self.params['secret']}
        with self.settings(SERVER_ADMIN_SECRETKEYS=secrets):
            # None
            response = self.client.post(self.url, self.params, follow=True)
            self.assertEquals(response.status_code, 404)

            # Invalid
            response = self.client.post(self.url, self.params, follow=True)
            self.assertEquals(response.status_code, 404)

    def test_update_primary_and_thumb(self):
        self.params['metadata-wardenclyffe-id'] = '33210',

        secrets = {'http://testserver/': self.params['secret']}
        with self.settings(SERVER_ADMIN_SECRETKEYS=secrets):
            # invalid primary source
            response = self.client.post(self.url, self.params, follow=True)
            self.assertEquals(response.status_code, 400)

            # valid primary source
            self.params['mp4_pseudo'] = 'new primary'

            response = self.client.post(self.url, self.params, follow=True)
            self.assertEquals(response.status_code, 200)

            s = self.asset.primary
            self.assertEquals(s.label, 'mp4_pseudo')
            self.assertEquals(s.url, self.params['mp4_pseudo'])

            self.assertEquals(self.asset.thumb_url, 'new thumb')
