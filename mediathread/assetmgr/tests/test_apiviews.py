from rest_framework import status
from rest_framework.test import APITestCase
from django.urls import reverse

from mediathread.factories import (
    AssetFactory, UserFactory, MediathreadTestMixin
)
from mediathread.assetmgr.models import Asset
from mediathread.sequence.tests.mixins import LoggedInTestMixin


class AssetUpdateTestsAnon(MediathreadTestMixin, APITestCase):
    def test_create_sherdnote_as_anon(self):
        """
        Ensure we can't update this asset.
        """
        asset = AssetFactory(title='My Title', primary_source='image')
        url = reverse('asset-update', kwargs={'asset_id': asset.pk})
        response = self.client.put(url, {
            'title': 'asset title'
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        asset.refresh_from_db()
        self.assertEqual(Asset.objects.count(), 1)
        self.assertEqual(asset.title, 'My Title')


class AssetTestsAsNonAuthor(
        LoggedInTestMixin, MediathreadTestMixin, APITestCase):
    def setUp(self):
        super(AssetTestsAsNonAuthor, self).setUp()
        self.setup_sample_course()
        self.add_as_student(self.sample_course, self.u)
        self.author = UserFactory()
        self.add_as_student(self.sample_course, self.author)

    def test_update_title_on_asset_not_author(self):
        asset = AssetFactory(
            title='My Title',
            primary_source='image', author=self.author,
            course=self.sample_course)
        url = reverse('asset-update', kwargs={'asset_id': asset.pk})

        response = self.client.put(url, {
            'title': 'New Title'
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        asset.refresh_from_db()
        self.assertEqual(Asset.objects.count(), 1)
        self.assertEqual(asset.title, 'My Title')


class AssetTestsAsAuthor(
        LoggedInTestMixin, MediathreadTestMixin, APITestCase):
    def setUp(self):
        super(AssetTestsAsAuthor, self).setUp()
        self.setup_sample_course()
        self.add_as_student(self.sample_course, self.u)

    def test_update_title_on_asset(self):
        asset = AssetFactory(
            title='My Title',
            primary_source='image',
            author=self.u,
            course=self.sample_course)
        url = reverse('asset-update', kwargs={'asset_id': asset.pk})

        response = self.client.put(url, {
            'title': 'New Title'
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        asset.refresh_from_db()
        self.assertEqual(Asset.objects.count(), 1)
        self.assertEqual(asset.title, 'New Title')
