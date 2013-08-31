#pylint: disable-msg=R0904
from django.test import TestCase
from django.test.client import Client


class SimpleViewTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_index(self):
        # it should redirect us somewhere.
        response = self.client.get("/")
        self.assertEquals(response.status_code, 302)
        # for now, we don't care where. really, we
        # are just making sure it's not a 500 error
        # at this point

    def test_smoke(self):
        # run the smoketests. we don't care if they pass
        # or fail, we just want to make sure that the
        # smoketests themselves don't have an error
        response = self.client.get("/smoketest/")
        self.assertEquals(response.status_code, 200)
