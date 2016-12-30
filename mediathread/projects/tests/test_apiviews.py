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

    def test_list_by_project(self):
        psa = ProjectSequenceAssetFactory()

        url = '{}?project={}'.format(
            reverse('projectsequenceasset-list'), psa.id)

        # anonymous user
        r = self.client.get(url)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(r.data), 0)

        # project's author
        self.client.login(
            username=psa.project.author.username, password='test')
        r = self.client.get(url)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(r.data), 1)

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
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(r.data), 0)
