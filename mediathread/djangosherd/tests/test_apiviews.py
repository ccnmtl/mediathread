from rest_framework import status
from rest_framework.test import APITestCase
from django.urls import reverse

from mediathread.factories import AssetFactory, MediathreadTestMixin
from mediathread.djangosherd.models import SherdNote
from mediathread.sequence.tests.mixins import LoggedInTestMixin


class SherdNoteTestsAnon(MediathreadTestMixin, APITestCase):
    def test_create_sherdnote_as_anon(self):
        """
        Ensure we can create a new SherdNote (annotation) object.
        """
        asset = AssetFactory(primary_source='image')
        url = reverse('sherdnote-create', kwargs={'asset_id': asset.pk})
        data = {
            'title': 'note title',
            'body': 'note body'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(SherdNote.objects.count(), 0)


class SherdNoteTestsAsStudent(
        LoggedInTestMixin, MediathreadTestMixin, APITestCase):
    def setUp(self):
        super(SherdNoteTestsAsStudent, self).setUp()
        self.setup_sample_course()
        self.add_as_student(self.sample_course, self.u)

    def test_create_sherdnote_on_own_asset(self):
        """
        Ensure we can create a new SherdNote (annotation) object.
        """
        asset = AssetFactory(
            primary_source='image', author=self.u, course=self.sample_course)
        url = reverse('sherdnote-create', kwargs={'asset_id': asset.pk})

        response = self.client.post(url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST,
                         'Empty POST data fails')

        data = {
            'title': 'note title',
            'body': 'note body',
            'range1': 23,
            'range2': 27.565,
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(SherdNote.objects.count(), 1)
        note = SherdNote.objects.get()
        self.assertEqual(note.title, 'note title')
        self.assertEqual(note.body, 'note body')
        self.assertEqual(note.range1, 23)
        self.assertEqual(note.range2, 27.565)
        self.assertEqual(note.author, self.u)

    def test_create_sherdnote_on_asset_not_visible(self):
        asset = AssetFactory(primary_source='image')
        url = reverse('sherdnote-create', kwargs={'asset_id': asset.pk})
        data = {
            'title': 'note title',
            'body': 'note body',
            'range1': 23,
            'range2': 27,
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
            'Can\'t create SherdNote on an asset that\'s not visible to me.'
        )
        self.assertEqual(SherdNote.objects.count(), 0)
