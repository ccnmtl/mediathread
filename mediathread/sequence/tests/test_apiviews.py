from django.core.urlresolvers import reverse
from rest_framework.test import APITestCase
from courseaffils.tests.factories import CourseFactory
from mediathread.factories import SherdNoteFactory, UserFactory, ProjectFactory
from mediathread.projects.models import ProjectSequenceAsset
from mediathread.sequence.models import (
    SequenceAsset, SequenceTextElement, SequenceMediaElement
)
from mediathread.sequence.tests.mixins import LoggedInTestMixin
from mediathread.projects.tests.factories import ProjectSequenceAssetFactory
from mediathread.sequence.tests.factories import (
    SequenceAssetFactory, SequenceTextElementFactory,
    SequenceMediaElementFactory
)


class AssetViewSetTest(LoggedInTestMixin, APITestCase):
    def test_list(self):
        SequenceAssetFactory(author=self.u)
        SequenceAssetFactory(author=self.u)
        SequenceAssetFactory(author=self.u)
        SequenceAssetFactory()

        r = self.client.get(reverse('sequenceasset-list'), format='json')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(r.data), 4)

    def test_retrieve(self):
        asset = SequenceAssetFactory(author=self.u)
        r = self.client.get(
            reverse('sequenceasset-detail', args=(asset.pk,)), format='json'
        )
        self.assertEqual(r.status_code, 200)
        self.assertIsNone(r.data.get('spine'))
        self.assertEqual(r.data.get('id'), asset.pk)

        note = SherdNoteFactory()
        asset = SequenceAssetFactory(author=self.u, spine=note)
        r = self.client.get(
            reverse('sequenceasset-detail', args=(asset.pk,)), format='json'
        )
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data.get('spine'), note.pk)

    def test_retrieve_with_text_elements(self):
        note = SherdNoteFactory()
        asset = SequenceAssetFactory(author=self.u, spine=note)
        e1 = SequenceTextElementFactory(sequence_asset=asset)
        e2 = SequenceTextElementFactory(sequence_asset=asset)
        e3 = SequenceTextElementFactory(sequence_asset=asset)
        r = self.client.get(
            reverse('sequenceasset-detail', args=(asset.pk,)), format='json'
        )
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data.get('spine'), note.pk)
        textelements = r.data.get('text_elements')
        self.assertEqual(textelements[0]['text'], e1.text)
        self.assertEqual(textelements[1]['text'], e2.text)
        self.assertEqual(textelements[2]['text'], e3.text)

    def test_retrieve_with_media_elements(self):
        note = SherdNoteFactory()
        asset = SequenceAssetFactory(author=self.u, spine=note)
        e1 = SequenceMediaElementFactory(sequence_asset=asset)
        e2 = SequenceMediaElementFactory(sequence_asset=asset)
        e3 = SequenceMediaElementFactory(sequence_asset=asset)
        r = self.client.get(
            reverse('sequenceasset-detail', args=(asset.pk,)), format='json'
        )
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data.get('spine'), note.pk)
        mediaelements = r.data.get('media_elements')
        self.assertEqual(mediaelements[0]['media'], e1.media.pk)
        self.assertEqual(mediaelements[1]['media'], e2.media.pk)
        self.assertEqual(mediaelements[2]['media'], e3.media.pk)

    def test_create(self):
        course = CourseFactory()
        note = SherdNoteFactory()
        project = ProjectFactory()
        r = self.client.post(
            reverse('sequenceasset-list'),
            {
                'course': course.pk,
                'spine': note.pk,
                'project': project.pk,
                'media_elements': [],
                'text_elements': [],
            }, format='json')

        self.assertEqual(r.status_code, 201)

        sa = SequenceAsset.objects.first()
        self.assertEqual(sa.course, sa.course)
        self.assertEqual(sa.author, self.u)
        self.assertEqual(sa.spine, note)

        self.assertEqual(ProjectSequenceAsset.objects.count(), 1)
        psa = ProjectSequenceAsset.objects.first()
        self.assertEqual(psa.sequence_asset, sa)
        self.assertEqual(psa.project, project)

    def test_create_with_track_elements(self):
        course = CourseFactory()
        note = SherdNoteFactory()
        project = ProjectFactory()
        r = self.client.post(
            reverse('sequenceasset-list'),
            {
                'course': course.pk,
                'spine': note.pk,
                'project': project.pk,
                'media_elements': [
                ],
                'text_elements': [
                    {
                        'text': 'My text',
                        'start_time': 0,
                        'end_time': 10,
                    }
                ]
            }, format='json')

        self.assertEqual(r.status_code, 201)

        sa = SequenceAsset.objects.first()
        self.assertEqual(sa.course, sa.course)
        self.assertEqual(sa.author, self.u)
        self.assertEqual(sa.spine, note)

        self.assertEqual(ProjectSequenceAsset.objects.count(), 1)
        psa = ProjectSequenceAsset.objects.first()
        self.assertEqual(psa.sequence_asset, sa)
        self.assertEqual(psa.project, project)

        self.assertEqual(SequenceTextElement.objects.count(), 1)

    def test_create_duplicate(self):
        course = CourseFactory()
        note = SherdNoteFactory()
        project = ProjectFactory()
        r = self.client.post(
            reverse('sequenceasset-list'),
            {
                'course': course.pk,
                'spine': note.pk,
                'project': project.pk,
                'media_elements': [
                ],
                'text_elements': [
                    {
                        'text': 'My text',
                        'start_time': 0,
                        'end_time': 10,
                    }
                ]
            }, format='json')

        self.assertEqual(r.status_code, 201)

        sa = SequenceAsset.objects.first()
        self.assertEqual(sa.course, sa.course)
        self.assertEqual(sa.author, self.u)
        self.assertEqual(sa.spine, note)

        self.assertEqual(ProjectSequenceAsset.objects.count(), 1)
        psa = ProjectSequenceAsset.objects.first()
        self.assertEqual(psa.sequence_asset, sa)
        self.assertEqual(psa.project, project)

        self.assertEqual(SequenceTextElement.objects.count(), 1)

        r = self.client.post(
            reverse('sequenceasset-list'),
            {
                'course': course.pk,
                'spine': note.pk,
                'project': project.pk,
                'media_elements': [
                ],
                'text_elements': [
                    {
                        'text': 'My text',
                        'start_time': 0,
                        'end_time': 10,
                    }
                ]
            }, format='json')

        self.assertEqual(
            r.status_code, 400,
            'Creating two SequenceAssets for the same combination '
            'of author / project should be invalid.')
        self.assertEqual(SequenceAsset.objects.count(), 1)

    def test_create_without_spine(self):
        course = CourseFactory()
        project = ProjectFactory()
        r = self.client.post(
            reverse('sequenceasset-list'),
            {
                'course': course.pk,
                'spine': '',
                'project': project.pk,
                'media_elements': [],
                'text_elements': [],
            }, format='json')

        self.assertEqual(r.status_code, 201)

        sa = SequenceAsset.objects.first()
        self.assertEqual(sa.course, sa.course)
        self.assertEqual(sa.author, self.u)
        self.assertIsNone(sa.spine)

        self.assertEqual(ProjectSequenceAsset.objects.count(), 1)
        psa = ProjectSequenceAsset.objects.first()
        self.assertEqual(psa.sequence_asset, sa)
        self.assertEqual(psa.project, project)

    def test_create_without_spine_with_track_elements(self):
        course = CourseFactory()
        project = ProjectFactory()
        note = SherdNoteFactory()
        r = self.client.post(
            reverse('sequenceasset-list'),
            {
                'course': course.pk,
                'spine': '',
                'project': project.pk,
                'media_elements': [
                    {
                        'media': note.pk,
                        'start_time': 0,
                        'end_time': 10,
                    }
                ],
                'text_elements': [
                    {
                        'text': 'My text',
                        'start_time': 0,
                        'end_time': 10,
                    }
                ]
            }, format='json')

        self.assertEqual(
            r.status_code, 400,
            'Attempting to create a SequenceAsset without a spine but '
            'with track elements should be invalid.')

    def test_update(self):
        sa = SequenceAssetFactory(author=self.u)
        psa = ProjectSequenceAssetFactory(sequence_asset=sa)
        note = SherdNoteFactory()
        r = self.client.put(
            reverse('sequenceasset-detail', args=(sa.pk,)),
            {
                'course': sa.course.pk,
                'project': psa.project.pk,
                'spine': note.pk,
                'media_elements': [],
                'text_elements': [],
            }, format='json')

        self.assertEqual(r.status_code, 200)

        sa.refresh_from_db()
        self.assertEqual(sa.course, sa.course)
        self.assertEqual(sa.author, self.u)
        self.assertEqual(sa.spine, note)
        self.assertEqual(SequenceAsset.objects.count(), 1)
        self.assertEqual(ProjectSequenceAsset.objects.count(), 1)

    def test_update_someone_elses_sequence_asset(self):
        someone_else = UserFactory()
        sa = SequenceAssetFactory(author=someone_else)
        psa = ProjectSequenceAssetFactory(sequence_asset=sa)
        note = SherdNoteFactory()
        r = self.client.put(
            reverse('sequenceasset-detail', args=(sa.pk,)),
            {
                'course': sa.course.pk,
                'project': psa.project.pk,
                'spine': note.pk,
                'media_elements': [],
                'text_elements': [
                    {
                        'text': 'My text',
                        'start_time': 0,
                        'end_time': 10,
                    }
                ],
            }, format='json')

        self.assertEqual(r.status_code, 403)

        sa.refresh_from_db()
        self.assertEqual(sa.course, sa.course)
        self.assertEqual(sa.author, someone_else)
        self.assertEqual(sa.spine, None)
        self.assertEqual(SequenceAsset.objects.count(), 1)
        self.assertEqual(ProjectSequenceAsset.objects.count(), 1)
        self.assertEqual(SequenceTextElement.objects.count(), 0)

    def test_update_with_track_elements(self):
        sa = SequenceAssetFactory(author=self.u)
        psa = ProjectSequenceAssetFactory(sequence_asset=sa)
        note = SherdNoteFactory()
        element_note = SherdNoteFactory()
        r = self.client.put(
            reverse('sequenceasset-detail', args=(sa.pk,)),
            {
                'course': sa.course.pk,
                'project': psa.project.pk,
                'spine': note.pk,
                'media_elements': [
                    {
                        'media': element_note.pk,
                        'start_time': 0,
                        'end_time': 10,
                    }
                ],
                'text_elements': [
                    {
                        'text': 'My text',
                        'start_time': 0,
                        'end_time': 10,
                    }
                ]
            }, format='json')

        self.assertEqual(r.status_code, 200)

        sa.refresh_from_db()
        self.assertEqual(sa.course, sa.course)
        self.assertEqual(sa.author, self.u)
        self.assertEqual(sa.spine, note)

        self.assertEqual(SequenceMediaElement.objects.count(), 1)
        self.assertEqual(SequenceTextElement.objects.count(), 1)

        r = self.client.put(
            reverse('sequenceasset-detail', args=(sa.pk,)),
            {
                'course': sa.course.pk,
                'spine': note.pk,
                'media_elements': [
                    {
                        'media': element_note.pk,
                        'start_time': 0,
                        'end_time': 10,
                    }
                ],
                'text_elements': [
                    {
                        'text': 'My text',
                        'start_time': 0,
                        'end_time': 10,
                    }
                ]
            }, format='json')

        self.assertEqual(r.status_code, 200)

        sa.refresh_from_db()
        self.assertEqual(sa.course, sa.course)
        self.assertEqual(sa.author, self.u)
        self.assertEqual(sa.spine, note)

        self.assertEqual(SequenceMediaElement.objects.count(), 1)
        self.assertEqual(SequenceTextElement.objects.count(), 1)

    def test_update_with_overlapping_elements(self):
        sa = SequenceAssetFactory(author=self.u)
        note = SherdNoteFactory()
        r = self.client.put(
            reverse('sequenceasset-detail', args=(sa.pk,)),
            {
                'course': sa.course.pk,
                'spine': note.pk,
                'media_elements': [
                ],
                'text_elements': [
                    {
                        'text': 'My text',
                        'start_time': 0,
                        'end_time': 0.3,
                    },
                    {
                        'text': 'My text',
                        'start_time': 0.35,
                        'end_time': 0.5,
                    },
                    {
                        'text': 'My text',
                        'start_time': 0.55,
                        'end_time': 0.9,
                    },
                    {
                        'text': 'My text',
                        'start_time': 1,
                        'end_time': 11,
                    },
                    {
                        'text': 'Overlapping!',
                        'start_time': 2,
                        'end_time': 12,
                    }
                ]
            }, format='json')

        self.assertEqual(r.status_code, 400)
        self.assertEqual(SequenceTextElement.objects.count(), 0)

        note = SherdNoteFactory()
        media_note1 = SherdNoteFactory()
        media_note2 = SherdNoteFactory()
        r = self.client.put(
            reverse('sequenceasset-detail', args=(sa.pk,)),
            {
                'course': sa.course.pk,
                'spine': note.pk,
                'media_elements': [
                    {
                        'media': media_note1.pk,
                        'start_time': 0,
                        'end_time': 10,
                    },
                    {
                        'media': media_note2.pk,
                        'start_time': 1,
                        'end_time': 11,
                    }
                ],
                'text_elements': [
                ]
            }, format='json')

        self.assertEqual(r.status_code, 400)
        self.assertEqual(SequenceMediaElement.objects.count(), 0)


class AssetViewSetUnAuthedTest(APITestCase):
    def test_list(self):
        SequenceAssetFactory()
        SequenceAssetFactory()

        r = self.client.get(reverse('sequenceasset-list'), format='json')
        self.assertEqual(r.status_code, 403)

    def test_create(self):
        course = CourseFactory()
        author = UserFactory()
        note = SherdNoteFactory()
        r = self.client.post(
            reverse('sequenceasset-list'),
            {
                'course': course.pk,
                'author': author.pk,
                'spine': note.pk,
                'media_elements': [],
                'text_elements': [],
            }, format='json')

        self.assertEqual(r.status_code, 403)

    def test_update(self):
        author = UserFactory()
        sa = SequenceAssetFactory(author=author)
        note = SherdNoteFactory()
        r = self.client.put(
            reverse('sequenceasset-detail', args=(sa.pk,)),
            {
                'course': sa.course.pk,
                'author': sa.author.pk,
                'spine': note.pk,
                'media_elements': [],
                'text_elements': [],
            }, format='json')

        self.assertEqual(r.status_code, 403)
