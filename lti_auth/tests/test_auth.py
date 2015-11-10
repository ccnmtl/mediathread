from django.test.testcases import TestCase
from pylti.common import LTI_SESSION_KEY

from lti_auth.auth import LTIBackend
from lti_auth.lti import LTI
from lti_auth.tests.factories import BASE_LTI_PARAMS, CONSUMERS, \
    generate_lti_request, LTICourseContextFactory, UserFactory


class LTIBackendTest(TestCase):

    def setUp(self):
        self.backend = LTIBackend()
        self.lti = LTI('initial', 'any')
        self.lti.lti_params = BASE_LTI_PARAMS.copy()

    def test_create_user(self):
        user = self.backend.create_user(self.lti, '12345')
        self.assertFalse(user.has_usable_password())
        self.assertEquals(user.email, 'foo@bar.com')
        self.assertEquals(user.get_full_name(), 'Foo Baz')

    def test_create_user_no_full_name(self):
        self.lti.lti_params.pop('lis_person_name_full')
        user = self.backend.create_user(self.lti, '12345')
        self.assertEquals(user.get_full_name(), 'student')

    def test_create_user_empty_full_name(self):
        self.lti.lti_params['lis_person_name_full'] = ''
        user = self.backend.create_user(self.lti, '12345')
        self.assertEquals(user.get_full_name(), 'student')

    def test_create_user_long_name(self):
        self.lti.lti_params['lis_person_name_full'] = (
            'Pneumonoultramicroscopicsilicovolcanoconiosis '
            'Supercalifragilisticexpialidocious')
        user = self.backend.create_user(self.lti, '12345')
        self.assertEquals(
            user.get_full_name(),
            'Pneumonoultramicroscopicsilico Supercalifragilisticexpialidoc')

    def test_find_or_create_user1(self):
        # via email
        user = UserFactory(email='foo@bar.com')
        self.assertEquals(self.backend.find_or_create_user(self.lti), user)

    def test_find_or_create_user2(self):
        # via hashed username
        self.lti.lti_params['oauth_consumer_key'] = '1234567890'
        username = self.backend.get_hashed_username(self.lti)
        user = UserFactory(username=username)
        self.assertEquals(self.backend.find_or_create_user(self.lti), user)

    def test_find_or_create_user3(self):
        # new user
        self.lti.lti_params['oauth_consumer_key'] = '1234567890'
        user = self.backend.find_or_create_user(self.lti)
        self.assertFalse(user.has_usable_password())
        self.assertEquals(user.email, 'foo@bar.com')
        self.assertEquals(user.get_full_name(), 'Foo Baz')

        username = self.backend.get_hashed_username(self.lti)
        self.assertEquals(user.username, username)

    def test_join_groups(self):
        ctx = LTICourseContextFactory()
        user = UserFactory()

        self.backend.join_groups(self.lti, ctx, user)
        self.assertTrue(user in ctx.group.user_set.all())
        self.assertTrue(user in ctx.faculty_group.user_set.all())

    def test_authenticate_invalid_course(self):
        with self.settings(PYLTI_CONFIG={'consumers': CONSUMERS}):
            request = generate_lti_request()
            self.assertIsNone(self.backend.authenticate(request=request,
                                                        request_type='initial',
                                                        role_type='any'))
            self.assertFalse(request.session[LTI_SESSION_KEY])

    def test_authenticate_valid_course(self):
        ctx = LTICourseContextFactory()

        with self.settings(PYLTI_CONFIG={'consumers': CONSUMERS}):
            request = generate_lti_request()
            user = self.backend.authenticate(request=request,
                                             request_type='initial',
                                             role_type='any')

            self.assertTrue(request.session[LTI_SESSION_KEY])
            self.assertFalse(user.has_usable_password())
            self.assertEquals(user.email, 'foo@bar.com')
            self.assertEquals(user.get_full_name(), 'Foo Baz')
            self.assertTrue(user in ctx.group.user_set.all())
            self.assertTrue(user in ctx.faculty_group.user_set.all())

    def test_get_user(self):
        user = UserFactory()
        self.assertIsNone(self.backend.get_user(1234))
        self.assertEquals(self.backend.get_user(user.id), user)
