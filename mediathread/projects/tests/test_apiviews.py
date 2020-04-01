from django.urls import reverse
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


class ProjectSequenceAssetViewSetUnAuthedTest(APITestCase):
    def test_list(self):
        ProjectSequenceAssetFactory()
        ProjectSequenceAssetFactory()

        r = self.client.get(reverse('projectsequenceasset-list'))
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(r.data), 0)
