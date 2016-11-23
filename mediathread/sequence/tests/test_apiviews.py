from django.core.urlresolvers import reverse
from rest_framework.test import APITestCase
from courseaffils.tests.factories import CourseFactory
from mediathread.factories import SherdNoteFactory, UserFactory, ProjectFactory
from mediathread.projects.models import ProjectSequenceAsset
from mediathread.sequence.models import SequenceAsset
from mediathread.sequence.tests.mixins import LoggedInTestMixin
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

        r = self.client.get(reverse('sequenceasset-list'))
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(r.data), 4)

    def test_retrieve(self):
        asset = SequenceAssetFactory(author=self.u)
        r = self.client.get(
            reverse('sequenceasset-detail', args=(asset.pk,))
        )
        self.assertEqual(r.status_code, 200)
        self.assertIsNone(r.data.get('spine'))

        note = SherdNoteFactory()
        asset = SequenceAssetFactory(author=self.u, spine=note)
        r = self.client.get(
            reverse('sequenceasset-detail', args=(asset.pk,))
        )
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data.get('spine'), note.pk)

    def test_retrieve_with_text_elements(self):
        note = SherdNoteFactory()
        asset = SequenceAssetFactory(author=self.u, spine=note)
        e1 = SequenceTextElementFactory(juxtaposition=asset)
        e2 = SequenceTextElementFactory(juxtaposition=asset)
        e3 = SequenceTextElementFactory(juxtaposition=asset)
        r = self.client.get(
            reverse('sequenceasset-detail', args=(asset.pk,))
        )
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data.get('spine'), note.pk)
        textelements = r.data.get('sequencetextelement_set')
        self.assertEqual(textelements[0]['text'], e1.text)
        self.assertEqual(textelements[1]['text'], e2.text)
        self.assertEqual(textelements[2]['text'], e3.text)

    def test_retrieve_with_media_elements(self):
        note = SherdNoteFactory()
        asset = SequenceAssetFactory(author=self.u, spine=note)
        e1 = SequenceMediaElementFactory(juxtaposition=asset)
        e2 = SequenceMediaElementFactory(juxtaposition=asset)
        e3 = SequenceMediaElementFactory(juxtaposition=asset)
        r = self.client.get(
            reverse('sequenceasset-detail', args=(asset.pk,))
        )
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data.get('spine'), note.pk)
        mediaelements = r.data.get('sequencemediaelement_set')
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
            })

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
                'sequencemediaelement_set': [
                ],
                'sequencetextelement_set': [
                    {
                        'text': 'My text',
                        'start_time': 0,
                        'end_time': 10,
                    }
                ]
            })

        self.assertEqual(r.status_code, 201)

        sa = SequenceAsset.objects.first()
        self.assertEqual(sa.course, sa.course)
        self.assertEqual(sa.author, self.u)
        self.assertEqual(sa.spine, note)

        self.assertEqual(ProjectSequenceAsset.objects.count(), 1)
        psa = ProjectSequenceAsset.objects.first()
        self.assertEqual(psa.sequence_asset, sa)
        self.assertEqual(psa.project, project)

        # TODO
        # self.assertEqual(SequenceTextElement.objects.count(), 1)

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
                'sequencemediaelement_set': [
                ],
                'sequencetextelement_set': [
                    {
                        'text': 'My text',
                        'start_time': 0,
                        'end_time': 10,
                    }
                ]
            })

        self.assertEqual(r.status_code, 201)

        sa = SequenceAsset.objects.first()
        self.assertEqual(sa.course, sa.course)
        self.assertEqual(sa.author, self.u)
        self.assertEqual(sa.spine, note)

        self.assertEqual(ProjectSequenceAsset.objects.count(), 1)
        psa = ProjectSequenceAsset.objects.first()
        self.assertEqual(psa.sequence_asset, sa)
        self.assertEqual(psa.project, project)

        # TODO
        # self.assertEqual(SequenceTextElement.objects.count(), 1)

        r = self.client.post(
            reverse('sequenceasset-list'),
            {
                'course': course.pk,
                'spine': note.pk,
                'project': project.pk,
                'sequencemediaelement_set': [
                ],
                'sequencetextelement_set': [
                    {
                        'text': 'My text',
                        'start_time': 0,
                        'end_time': 10,
                    }
                ]
            })

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
            })

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
        self.client.post(
            reverse('sequenceasset-list'),
            {
                'course': course.pk,
                'spine': '',
                'project': project.pk,
                'sequencemediaelement_set': [
                    {
                        'media': note.pk,
                        'start_time': 0,
                        'end_time': 10,
                    }
                ],
                'sequencetextelement_set': [
                    {
                        'text': 'My text',
                        'start_time': 0,
                        'end_time': 10,
                    }
                ]
            })

        # TODO
        # self.assertEqual(
        #     r.status_code, 400,
        #     'Attempting to create a SequenceAsset without a spine but '
        #     'with track elements should be invalid.')

    def test_update(self):
        sa = SequenceAssetFactory(author=self.u)
        note = SherdNoteFactory()
        r = self.client.put(
            reverse('sequenceasset-detail', args=(sa.pk,)),
            {
                'course': sa.course.pk,
                'spine': note.pk,
            })

        self.assertEqual(r.status_code, 200)

        sa.refresh_from_db()
        self.assertEqual(sa.course, sa.course)
        self.assertEqual(sa.author, self.u)
        self.assertEqual(sa.spine, note)


class AssetViewSetUnAuthedTest(APITestCase):
    def test_list(self):
        SequenceAssetFactory()
        SequenceAssetFactory()

        r = self.client.get(reverse('sequenceasset-list'))
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
            })

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
            })

        self.assertEqual(r.status_code, 403)
