from rest_framework import status
from rest_framework.test import APITestCase
from django.urls import reverse
from tagging.models import Tag

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
        self.assertEqual(SherdNote.objects.count(), 2)
        note = SherdNote.objects.get(title='note title')
        self.assertEqual(note.body, 'note body')
        self.assertEqual(note.range1, 23)
        self.assertEqual(note.range2, 27.565)
        self.assertEqual(note.author, self.u)

        data = {
            'title': 'note title 2',
            'body': 'note body 2',
            'range1': 43,
            'range2': 47.565,
            'tags': 'My Tag,Green,Black',
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(SherdNote.objects.count(), 3)
        note = SherdNote.objects.get(title='note title 2')
        self.assertEqual(note.body, 'note body 2')
        self.assertEqual(note.range1, 43)
        self.assertEqual(note.range2, 47.565)
        self.assertEqual(note.author, self.u)

        # test saved tag functionality
        tags = note.tags_split()
        self.assertEqual(len(tags), 3)
        Tag.objects.get(name='my tag')
        Tag.objects.get(name='green')
        Tag.objects.get(name='black')
        with self.assertRaises(Tag.DoesNotExist):
            Tag.objects.get(name='unknown tag')

    def test_create_sherdnote_that_starts_at_0(self):
        """
        Ensure we can create a new SherdNote (annotation) object.
        """
        asset = AssetFactory(
            primary_source='image', author=self.u, course=self.sample_course)
        url = reverse('sherdnote-create', kwargs={'asset_id': asset.pk})

        data = {
            'title': 'note title',
            'body': 'note body',
            'range1': 0,
            'range2': 17.565,
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(SherdNote.objects.count(), 2)
        note = SherdNote.objects.get(title='note title')
        self.assertEqual(note.body, 'note body')
        self.assertEqual(note.range1, 0)
        self.assertEqual(note.range2, 17.565)
        self.assertEqual(note.author, self.u)

    def test_create_sherdnote_on_classmates_asset(self):
        """
        Ensure we can create a new SherdNote (annotation) object on a
        classmate's asset.
        """
        asset = AssetFactory(
            primary_source='image', author=self.student_one,
            course=self.sample_course)
        url = reverse('sherdnote-create', kwargs={'asset_id': asset.pk})

        data = {
            'title': 'note title',
            'body': 'note body',
            'range1': 23,
            'range2': 27.565,
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(SherdNote.objects.count(), 2)
        note = SherdNote.objects.get(title='note title')
        self.assertEqual(note.author, self.u)

    def test_create_sherdnote_on_own_image_asset(self):
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
            'title': 'Image annotation',
            'body': 'Image annotation body',
            'range1': -2,
            'range2': -1,
            'annotation_data': {
                'geometry': {
                    'type': 'Polygon',
                    'coordinates': [
                        [
                            [
                                [276.88964843749994, 128.6806640625],
                                [323.78417968749994, 14.2275390625],
                                [435.80566406249994, 100.990234375],
                                [276.88964843749994, 128.6806640625]
                            ]
                        ]
                    ]
                },
                'default': False,
                'x': -2,
                'y': -1,
                'zoom': 1,
                'extent': [
                    276.88964843749994,
                    14.2275390625,
                    435.80566406249994,
                    128.6806640625
                ]
            }
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(SherdNote.objects.count(), 2)
        note = SherdNote.objects.get(title='Image annotation')
        self.assertEqual(note.body, 'Image annotation body')
        self.assertEqual(note.range1, -2)
        self.assertEqual(note.range2, -1)
        self.assertEqual(note.author, self.u)

        # Test annotation data (this saves/loads as JSON text)
        annotation_data = note.annotation()
        self.assertEqual(annotation_data['geometry']['type'], 'Polygon')
        self.assertEqual(
            annotation_data['geometry']['coordinates'][0][0][0],
            [276.88964843749994, 128.6806640625])
        self.assertEqual(
            annotation_data['extent'], [
                276.88964843749994,
                14.2275390625,
                435.80566406249994,
                128.6806640625
            ]
        )

    def test_create_sherdnote_with_tags_and_terms(self):
        """
        Ensure we can create a new SherdNote (annotation) object with
        tags and terms.
        """
        taxonomy = {
            'Shapes': ['Square', 'Triangle'],
            'Colors': ['Red', 'Blue', 'Green']
        }

        self.create_vocabularies(self.sample_course, taxonomy)

        vocab1 = self.sample_course.vocabulary_set.first()
        vocab2 = self.sample_course.vocabulary_set.last()
        term1 = vocab1.term_set.first()
        term2 = vocab1.term_set.all()[1]
        term3 = vocab2.term_set.last()

        asset = AssetFactory(
            primary_source='image', author=self.u, course=self.sample_course)
        url = reverse('sherdnote-create', kwargs={'asset_id': asset.pk})

        response = self.client.post(url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST,
                         'Empty POST data fails')

        data = {
            'title': 'Image annotation',
            'body': 'Image annotation body',
            'range1': -2,
            'range2': -1,
            'tags': 'tag1 tag2 abc',
            'terms': [term1.pk, term2.pk, term3.pk],
            'annotation_data': {
                'geometry': {
                    'type': 'Polygon',
                    'coordinates': [
                        [
                            [
                                [276.88964843749994, 128.6806640625],
                                [323.78417968749994, 14.2275390625],
                                [435.80566406249994, 100.990234375],
                                [276.88964843749994, 128.6806640625]
                            ]
                        ]
                    ]
                },
                'default': False,
                'x': -2,
                'y': -1,
                'zoom': 1,
                'extent': [
                    276.88964843749994,
                    14.2275390625,
                    435.80566406249994,
                    128.6806640625
                ]
            }
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(SherdNote.objects.count(), 2)
        note = SherdNote.objects.get(title='Image annotation')
        self.assertEqual(note.body, 'Image annotation body')
        self.assertEqual(note.range1, -2)
        self.assertEqual(note.range2, -1)
        self.assertEqual(note.author, self.u)
        self.assertEqual(note.tags, 'tag1 tag2 abc')
        self.assertEqual(len(note.termrelationship_set.all()), 3)

        # Test annotation data (this saves/loads as JSON text)
        annotation_data = note.annotation()
        self.assertEqual(annotation_data['geometry']['type'], 'Polygon')
        self.assertEqual(
            annotation_data['geometry']['coordinates'][0][0][0],
            [276.88964843749994, 128.6806640625])
        self.assertEqual(
            annotation_data['extent'], [
                276.88964843749994,
                14.2275390625,
                435.80566406249994,
                128.6806640625
            ]
        )

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
