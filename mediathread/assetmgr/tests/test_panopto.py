import mock
from mediathread.assetmgr.panopto import PanoptoApi
from django.test.testcases import TestCase


class PanoptoApiTest(TestCase):

    @classmethod
    def _mock_api(cls, name):
        return None

    def setUp(self):
        with mock.patch.object(PanoptoApi, '_api', new=self._mock_api):
            self.api = PanoptoApi()

    def test_user_key(self):
        with self.settings(PANOPTO_API_APP_ID='TEST'):
            self.assertEquals(self.api._user_key('foo'), 'TEST\\foo')

    def test_auth_code(self):
        with self.settings(PANOPTO_SERVER='http://localhost',
                           PANOPTO_API_TOKEN='1234'):
            self.assertIsNotNone(self.api._auth_code('TEST\\foo'))

    def test_auth_info(self):
        with self.settings(PANOPTO_API_APP_ID='TEST',
                           PANOPTO_SERVER='http://localhost',
                           PANOPTO_API_TOKEN='1234'):
            ai = self.api._auth_info('foo')
            self.assertEquals(ai['UserKey'], 'TEST\\foo')
            self.assertIsNotNone(ai['AuthCode'])
