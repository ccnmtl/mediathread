from smoketest import SmokeTest
from mediathread.main.models import UserSetting


class DBConnectivity(SmokeTest):
    def test_retrieve(self):
        cnt = UserSetting.objects.all().count()
        self.assertTrue(cnt > 0)
