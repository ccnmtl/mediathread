from django.test.testcases import TestCase

from lti_auth.auth import LTIBackend
from lti_auth.lti import LTI
from mediathread.factories import UserFactory, CourseFactory


class LTIBackendTest(TestCase):
    lti_params = {
        'oauth_consumer_key': '1234567890',
        'user_id': 'student_one',
        'lis_person_contact_email_primary': 'foo@bar.com',
        'lis_person_name_full': 'Foo Bar Baz',
        'roles': 'Instructor,Staff',
        'custom_course_group':
            't3.y2011.s001.ce0001.aaaa.st.course:columbia.edu',
    }

    def setUp(self):
        self.backend = LTIBackend()
        self.lti = LTI('initial', 'any')
        self.lti.lti_params = self.lti_params

    def test_create_user(self):
        user = self.backend.create_user(self.lti, '12345')
        self.assertFalse(user.has_usable_password())
        self.assertEquals(user.email, 'foo@bar.com')
        self.assertEquals(user.get_full_name(), 'Foo Bar Baz')

    def test_find_or_create_user1(self):
        # via email
        user = UserFactory(email='foo@bar.com')
        self.assertEquals(self.backend.find_or_create_user(self.lti), user)

    def test_find_or_create_user2(self):
        # via hashed username
        username = self.backend.get_hashed_username(self.lti)
        user = UserFactory(username=username)
        self.assertEquals(self.backend.find_or_create_user(self.lti), user)

    def test_find_or_create_user3(self):
        # new user
        user = self.backend.find_or_create_user(self.lti)
        self.assertFalse(user.has_usable_password())
        self.assertEquals(user.email, 'foo@bar.com')
        self.assertEquals(user.get_full_name(), 'Foo Bar Baz')

        username = self.backend.get_hashed_username(self.lti)
        self.assertEquals(user.username, username)

    def test_join_course(self):
        course = CourseFactory()
        user = UserFactory()

        self.backend.join_course(self.lti, course, user)
        self.assertTrue(course.is_member(user))
        self.assertTrue(course.is_faculty(user))

    def test_authenticate(self):
        pass  # @todo

    def test_get_user(self):
        user = UserFactory()
        self.assertIsNone(self.backend.get_user(1234))
        self.assertEquals(self.backend.get_user(user.id), user)
