from __future__ import unicode_literals

from django.test.testcases import TestCase
from django.utils.encoding import smart_str

from mediathread.factories import (
    MediathreadTestMixin, UserFactory, UserProfileFactory,
)
from mediathread.main.models import UserSetting


class UserSettingsTest(MediathreadTestMixin, TestCase):

    def setUp(self):
        self.setup_sample_course()

    def test_get_setting_default_value(self):
        self.assertEqual(UserSetting.get_setting(self.student_one, '1', 0), 0)

    def test_get_setting(self):
        # default - name='Test', value=1
        UserSetting.set_setting(self.student_one, 'Test', value=1)
        self.assertEqual(UserSetting.get_setting(self.student_one, 'Test', 0),
                         '1')

        UserSetting.set_setting(self.student_one, 'Test', value='True')
        self.assertTrue(UserSetting.get_setting(self.student_one, 'Test', 0))
        UserSetting.set_setting(self.student_one, 'Test', value='true')
        self.assertTrue(UserSetting.get_setting(self.student_one, 'Test', 0))

        UserSetting.set_setting(self.student_one, 'Test', value='False')
        self.assertFalse(UserSetting.get_setting(self.student_one, 'Test', 0))
        UserSetting.set_setting(self.student_one, 'Test', value='false')
        self.assertFalse(UserSetting.get_setting(self.student_one, 'Test', 0))


class UserProfileTest(TestCase):

    def test_unicode(self):
        user = UserFactory(username='johndoe')
        profile = UserProfileFactory(user=user)
        self.assertEqual(smart_str(profile), 'johndoe')
