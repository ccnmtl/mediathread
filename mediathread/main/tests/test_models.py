from django.test.client import RequestFactory
from django.test.testcases import TestCase

from mediathread.factories import (
    MediathreadTestMixin, UserFactory, UserProfileFactory, CourseFactory,
    AffilFactory
)
from mediathread.main.models import (
    UserSetting, user_registered_callback,
    user_activated_callback
)


class UserSettingsTest(MediathreadTestMixin, TestCase):

    def setUp(self):
        self.setup_sample_course()

    def test_get_setting_default_value(self):
        self.assertEquals(UserSetting.get_setting(self.student_one, '1', 0), 0)

    def test_get_setting(self):
        # default - name='Test', value=1
        UserSetting.set_setting(self.student_one, 'Test', value=1)
        self.assertEquals(UserSetting.get_setting(self.student_one, 'Test', 0),
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
        self.assertEquals(profile.__unicode__(), 'johndoe')


class UserRegistrationTest(TestCase):
    def test_user_registered_callback(self):
        user = UserFactory()
        data = {'first_name': 'John',
                'last_name': 'Doe',
                'title': 'Professor',
                'institution': 'Columbia University',
                'referred_by': 'Sam Smith',
                'user_story': 'Sample user story'}

        request = RequestFactory().post('/', data)
        user_registered_callback(None, user, request)

        user.refresh_from_db()
        self.assertEquals(user.first_name, 'John')
        self.assertEquals(user.last_name, 'Doe')
        self.assertEquals(user.profile.title, 'Professor')
        self.assertEquals(user.profile.institution, 'Columbia University')
        self.assertEquals(user.profile.referred_by, 'Sam Smith')
        self.assertEquals(user.profile.user_story, 'Sample user story')

    def test_user_activated_callback(self):
        course = CourseFactory(title='Mediathread Guest Sandbox')
        user = UserFactory()

        user_activated_callback(None, user, None)

        self.assertTrue(course.is_member(user))


class AffilTest(TestCase):
    def setUp(self):
        self.aa = AffilFactory()

    def test_is_valid_from_factory(self):
        self.aa.full_clean()
