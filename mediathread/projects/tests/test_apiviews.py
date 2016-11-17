from django.core.urlresolvers import reverse
from rest_framework.test import APITestCase
from mediathread.projects.tests.factories import ProjectSequenceAssetFactory
from mediathread.sequence.tests.factories import SequenceAssetFactory
from mediathread.sequence.tests.mixins import LoggedInTestMixin


class ProjectSequenceAssetViewSetTest(LoggedInTestMixin, APITestCase):
    def test_list(self):
        ProjectSequenceAssetFactory(
            sequence_asset=SequenceAssetFactory(author=self.u))
        ProjectSequenceAssetFactory(
            sequence_asset=SequenceAssetFactory(author=self.u))
        ProjectSequenceAssetFactory(
            sequence_asset=SequenceAssetFactory(author=self.u))
        ProjectSequenceAssetFactory()

        r = self.client.get(reverse('projectsequenceasset-list'))
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(r.data), 3)

    def test_retrieve(self):
        psa = ProjectSequenceAssetFactory()
        r = self.client.get(
            reverse('projectsequenceasset-detail', args=(psa.pk,)))
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(r.data), 3)
        self.assertEqual(r.data['project'], psa.project.pk)


class ProjectSequenceAssetViewSetUnAuthedTest(APITestCase):
    def test_list(self):
        ProjectSequenceAssetFactory()
        ProjectSequenceAssetFactory()

        r = self.client.get(reverse('projectsequenceasset-list'))
        self.assertEqual(r.status_code, 403)
