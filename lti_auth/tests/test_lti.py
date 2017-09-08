from django.test.client import RequestFactory
from django.test.testcases import TestCase
from pylti.common import LTI_SESSION_KEY, LTINotInSessionException

from lti_auth.lti import LTI
from lti_auth.tests.factories import BASE_LTI_PARAMS, CONSUMERS, \
    generate_lti_request


class LTITest(TestCase):

    def test_init(self):
        lti = LTI('initial', 'any')
        self.assertEquals(lti.request_type, 'initial')
        self.assertEquals(lti.role_type, 'any')

    def test_consumer_user_id(self):
        lti = LTI('initial', 'any')
        lti.lti_params = BASE_LTI_PARAMS.copy()
        lti.lti_params['oauth_consumer_key'] = '1234567890'

        self.assertEquals(lti.consumer_user_id(), '1234567890-student')

    def test_user_email(self):
        lti = LTI('initial', 'any')
        self.assertIsNone(lti.user_email())

        lti.lti_params = BASE_LTI_PARAMS
        self.assertEquals(lti.user_email(), 'foo@bar.com')

    def test_user_fullname(self):
        lti = LTI('initial', 'any')
        self.assertEquals(lti.user_fullname(), '')

        lti.lti_params = {'user_id': 'student_one'}
        self.assertEquals(lti.user_fullname(), 'student_one')

        lti.lti_params = BASE_LTI_PARAMS
        self.assertEquals(lti.user_fullname(), 'Foo Bar Baz')

    def test_user_roles(self):
        lti = LTI('initial', 'any')
        self.assertEquals(lti.user_roles(), [])

        lti.lti_params = BASE_LTI_PARAMS
        self.assertEquals(lti.user_roles(), [
            u'urn:lti:instrole:ims/lis/instructor',
            u'urn:lti:instrole:ims/lis/staff'])

        self.assertTrue(lti.is_instructor())
        self.assertFalse(lti.is_administrator())

    def test_consumers(self):
        lti = LTI('any', 'any')

        with self.settings(PYLTI_CONFIG={'consumers': CONSUMERS}):
            self.assertEquals(lti._consumers(), CONSUMERS)

    def test_verify_any(self):
        lti = LTI('any', 'any')
        request = generate_lti_request()

        with self.settings(PYLTI_CONFIG={'consumers': CONSUMERS}):
            # test_verify_request
            lti.verify(request)
            self.assertTrue(request.session[LTI_SESSION_KEY])

            # test_verify_session
            self.assertTrue(lti.verify(request))

    def test_verify_session(self):
        lti = LTI('session', 'any')
        request = RequestFactory().post('/lti/')

        with self.assertRaises(LTINotInSessionException):
            request.session = {}
            lti.verify(request)

        request.session = {LTI_SESSION_KEY: True}
        self.assertTrue(lti.verify(request))

    def test_verify_request(self):
        with self.settings(PYLTI_CONFIG={'consumers': CONSUMERS}):
            request = generate_lti_request()
            lti = LTI('initial', 'any')
            lti.verify(request)
            self.assertTrue(request.session[LTI_SESSION_KEY])
