from decimal import Decimal
from json import loads

from courseaffils.tests.factories import CourseFactory
from django.urls import reverse
from rest_framework.test import APITestCase

from mediathread.factories import SherdNoteFactory, UserFactory, ProjectFactory
from mediathread.projects.models import ProjectSequenceAsset
from mediathread.projects.tests.factories import ProjectSequenceAssetFactory
from mediathread.sequence.models import (
    SequenceAsset, SequenceTextElement, SequenceMediaElement
)
from mediathread.sequence.tests.factories import (
    SequenceAssetFactory, SequenceTextElementFactory,
    SequenceMediaElementFactory
)
from mediathread.sequence.tests.mixins import LoggedInTestMixin


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
        the_json = loads(r.content)
        self.assertEqual(the_json['spine']['id'], note.pk)
        self.assertEqual(the_json['spine_asset'], note.asset.pk)

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
        the_json = loads(r.content)
        self.assertEqual(the_json['spine']['id'], note.pk)
        textelements = the_json['text_elements']
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

        the_json = loads(r.content)
        self.assertEqual(the_json['spine']['id'], note.pk)

        mediaelements = the_json['media_elements']
        self.assertEqual(mediaelements[0]['media']['id'], e1.media.pk)
        self.assertEqual(mediaelements[0]['media_asset'], e1.media.asset.pk)
        self.assertEqual(mediaelements[1]['media']['id'], e2.media.pk)
        self.assertEqual(mediaelements[2]['media']['id'], e3.media.pk)

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
                        'start_time': Decimal('0'),
                        'end_time': Decimal('10'),
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

    def test_create_with_track_elements_with_large_decimals(self):
        course = CourseFactory()
        note = SherdNoteFactory()
        note2 = SherdNoteFactory()
        project = ProjectFactory()
        r = self.client.post(
            reverse('sequenceasset-list'),
            {
                'course': course.pk,
                'spine': note.pk,
                'project': project.pk,
                'media_elements': [
                    {
                        'media': note2.pk,
                        'start_time': Decimal('0.9999999999992222'),
                        'end_time': Decimal('10.15955395959359395'),
                    }
                ],
                'text_elements': [
                    {
                        'text': 'My text',
                        'start_time': Decimal('0.19898591249142984912849218'),
                        'end_time': Decimal('10.853598923859285928598958392'),
                    },
                    {
                        'text': 'My text 2',
                        'start_time': Decimal('11'),
                        'end_time': Decimal('148744.835739573575'),
                    },
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

        self.assertEqual(SequenceTextElement.objects.count(), 2)
        e0 = SequenceTextElement.objects.first()
        e1 = SequenceTextElement.objects.last()
        self.assertEqual(e0.text, 'My text')
        self.assertEqual(e0.start_time, Decimal('0.19899'))
        self.assertEqual(e0.end_time, Decimal('10.85360'))
        self.assertEqual(e1.text, 'My text 2')
        self.assertEqual(e1.start_time, Decimal('11'))
        self.assertEqual(e1.end_time, Decimal('148744.83574'))

        self.assertEqual(SequenceMediaElement.objects.count(), 1)
        e0 = SequenceMediaElement.objects.first()
        self.assertEqual(e0.media, note2)
        self.assertEqual(e0.start_time, Decimal('1.00000'))
        self.assertEqual(e0.end_time, Decimal('10.15955'))

    def test_create_with_track_elements_with_no_end_time(self):
        course = CourseFactory()
        note = SherdNoteFactory()
        note2 = SherdNoteFactory()
        project = ProjectFactory()
        r = self.client.post(
            reverse('sequenceasset-list'),
            {
                'course': course.pk,
                'spine': note.pk,
                'project': project.pk,
                'media_elements': [
                    {
                        'media': note2.pk,
                        'start_time': Decimal('0.9999'),
                        'end_time': None,
                    }
                ],
                'text_elements': [
                    {
                        'text': 'My text',
                        'start_time': Decimal('0.198985'),
                        'end_time': None,
                    },
                    {
                        'text': 'My text 2',
                        'start_time': Decimal('11'),
                        'end_time': Decimal('14'),
                    },
                ]
            }, format='json')

        self.assertEqual(
            r.status_code, 400,
            'Attempting to create track elements with no end time should '
            'be invalid.')

    def test_create_with_track_elements_with_no_start_time(self):
        course = CourseFactory()
        note = SherdNoteFactory()
        note2 = SherdNoteFactory()
        project = ProjectFactory()
        r = self.client.post(
            reverse('sequenceasset-list'),
            {
                'course': course.pk,
                'spine': note.pk,
                'project': project.pk,
                'media_elements': [
                    {
                        'media': note2.pk,
                        'start_time': None,
                        'end_time': Decimal('0.9999'),
                    }
                ],
                'text_elements': [
                    {
                        'text': 'My text',
                        'start_time': None,
                        'end_time': Decimal('0.198985'),
                    },
                    {
                        'text': 'My text 2',
                        'start_time': Decimal('11'),
                        'end_time': Decimal('14'),
                    },
                ]
            }, format='json')

        self.assertEqual(
            r.status_code, 400,
            'Attempting to create track elements with no start time should '
            'be invalid.')

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
                        'start_time': Decimal('0'),
                        'end_time': Decimal('10'),
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
                        'start_time': Decimal('0'),
                        'end_time': Decimal('10'),
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
                'spine': None,
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
                        'start_time': Decimal('0'),
                        'end_time': Decimal('10'),
                    }
                ],
                'text_elements': [
                    {
                        'text': 'My text',
                        'start_time': Decimal('0'),
                        'end_time': Decimal('10'),
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
                'spine_volume': 100,
                'media_elements': [],
                'text_elements': [
                    {
                        'text': 'My text',
                        'start_time': Decimal('0'),
                        'end_time': Decimal('10'),
                    }
                ],
            }, format='json')

        self.assertEqual(r.status_code, 403)

        sa.refresh_from_db()
        self.assertEqual(sa.course, sa.course)
        self.assertEqual(sa.author, someone_else)
        self.assertEqual(sa.spine, None)
        self.assertEqual(sa.spine_volume, 80)
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
                'spine_volume': 0,
                'media_elements': [
                    {
                        'media': element_note.pk,
                        'start_time': Decimal('0'),
                        'end_time': Decimal('10'),
                        'volume': 0,
                    }
                ],
                'text_elements': [
                    {
                        'text': 'My text',
                        'start_time': Decimal('0'),
                        'end_time': Decimal('10'),
                    }
                ]
            }, format='json')

        self.assertEqual(r.status_code, 200)

        sa.refresh_from_db()
        self.assertEqual(sa.course, sa.course)
        self.assertEqual(sa.author, self.u)
        self.assertEqual(sa.spine, note)
        self.assertEqual(sa.spine_volume, 0)

        self.assertEqual(SequenceMediaElement.objects.count(), 1)
        element = SequenceMediaElement.objects.first()
        self.assertEqual(element.volume, 0)
        self.assertEqual(SequenceTextElement.objects.count(), 1)

        r = self.client.put(
            reverse('sequenceasset-detail', args=(sa.pk,)),
            {
                'course': sa.course.pk,
                'spine': note.pk,
                'spine_volume': 65,
                'media_elements': [
                    {
                        'media': element_note.pk,
                        'start_time': Decimal('0'),
                        'end_time': Decimal('10'),
                        'volume': 30,
                    }
                ],
                'text_elements': [
                    {
                        'text': 'My text',
                        'start_time': Decimal('0'),
                        'end_time': Decimal('10'),
                    },
                    {
                        'text': 'My text',
                        'start_time': Decimal('10'),
                        'end_time': Decimal('12'),
                    }
                ]
            }, format='json')

        self.assertEqual(r.status_code, 200)

        sa.refresh_from_db()
        self.assertEqual(sa.course, sa.course)
        self.assertEqual(sa.author, self.u)
        self.assertEqual(sa.spine, note)
        self.assertEqual(sa.spine_volume, 65)

        self.assertEqual(SequenceMediaElement.objects.count(), 1)
        element = SequenceMediaElement.objects.first()
        self.assertEqual(element.volume, 30)
        self.assertEqual(SequenceTextElement.objects.count(), 2)

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
                        'start_time': Decimal('0'),
                        'end_time': Decimal('0.3'),
                    },
                    {
                        'text': 'My text',
                        'start_time': Decimal('0.35'),
                        'end_time': Decimal('0.5'),
                    },
                    {
                        'text': 'My text',
                        'start_time': Decimal('0.55'),
                        'end_time': Decimal('0.9'),
                    },
                    {
                        'text': 'My text',
                        'start_time': Decimal('1'),
                        'end_time': Decimal('11'),
                    },
                    {
                        'text': 'Overlapping!',
                        'start_time': Decimal('2'),
                        'end_time': Decimal('12'),
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
                        'start_time': Decimal('0'),
                        'end_time': Decimal('10'),
                    },
                    {
                        'media': media_note2.pk,
                        'start_time': Decimal('1'),
                        'end_time': Decimal('11'),
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
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(r.data), 2)

    def test_retrieve(self):
        asset = SequenceAssetFactory()
        r = self.client.get(
            reverse('sequenceasset-detail', args=(asset.pk,)), format='json'
        )
        self.assertEqual(r.status_code, 200)
        self.assertIsNone(r.data.get('spine'))
        self.assertEqual(r.data.get('id'), asset.pk)

        note = SherdNoteFactory()
        asset = SequenceAssetFactory(spine=note)
        r = self.client.get(
            reverse('sequenceasset-detail', args=(asset.pk,)), format='json'
        )
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data.get('spine')['id'], note.pk)

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
