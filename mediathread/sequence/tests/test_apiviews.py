from django.core.urlresolvers import reverse
from rest_framework.test import APITestCase

from mediathread.factories import AssetFactory
from mediathread.sequence.tests.mixins import LoggedInTestMixin
from mediathread.sequence.tests.factories import SequenceAssetFactory


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

    def test_update(self):
        sa = SequenceAssetFactory(author=self.u)
        asset = AssetFactory(course=sa.course)
        r = self.client.put(
            reverse('sequenceasset-detail', args=(sa.pk,)),
            {
                'course': sa.course.pk,
                'author': sa.author.pk,
                'spine': asset.pk,
            })

        self.assertEqual(r.status_code, 200)

        sa.refresh_from_db()
        # TODO
        # self.assertEqual(sa.spine, asset)


class AssetViewSetUnAuthedTest(APITestCase):
    def test_list(self):
        SequenceAssetFactory()
        SequenceAssetFactory()

        r = self.client.get(reverse('sequenceasset-list'))
        self.assertEqual(r.status_code, 403)
