from django.test.client import RequestFactory
from django.test.testcases import TestCase
from pylti.common import LTI_SESSION_KEY, LTINotInSessionException

from lti_auth.lti import LTI


class LTITest(TestCase):
    lti_params = {
        'oauth_consumer_key': '1234567890',
        'user_id': 'student_one',
        'lis_person_contact_email_primary': 'foo@bar.com',
        'lis_person_name_full': 'Foo Bar Baz',
        'roles': 'Instructor,Staff',
        'custom_course_group':
            't3.y2011.s001.ce0001.aaaa.st.course:columbia.edu',
    }

    def test_init(self):
        lti = LTI('initial', 'any')
        self.assertEquals(lti.request_type, 'initial')
        self.assertEquals(lti.role_type, 'any')

    def test_consumer_user_id(self):
        lti = LTI('initial', 'any')
        lti.lti_params = self.lti_params

        self.assertEquals(lti.consumer_user_id(), '1234567890-student_one')

    def test_user_email(self):
        lti = LTI('initial', 'any')
        self.assertIsNone(lti.user_email())

        lti.lti_params = self.lti_params
        self.assertEquals(lti.user_email(), 'foo@bar.com')

    def test_user_fullname(self):
        lti = LTI('initial', 'any')
        self.assertEquals(lti.user_fullname(), '')

        lti.lti_params = {'user_id': 'student_one'}
        self.assertEquals(lti.user_fullname(), 'student_one')

        lti.lti_params = self.lti_params
        self.assertEquals(lti.user_fullname(), 'Foo Bar Baz')

    def test_user_roles(self):
        lti = LTI('initial', 'any')
        self.assertEquals(lti.user_roles(), [])

        lti.lti_params = self.lti_params
        self.assertEquals(lti.user_roles(), ['Instructor', 'Staff'])

    def test_course_group(self):
        lti = LTI('initial', 'any')
        self.assertEquals(lti.course_group(), None)

        lti.lti_params = self.lti_params
        self.assertEquals(lti.course_group(),
                          't3.y2011.s001.ce0001.aaaa.st.course:columbia.edu')

    def test_verify_any(self):
        lti = LTI('any', 'any')
        request = RequestFactory().post('/lti/')
        request.session = {LTI_SESSION_KEY: True}
        self.assertTrue(lti.verify(request))

        # @todo -- test the verify_request path

    def test_verify_session(self):
        lti = LTI('session', 'any')
        request = RequestFactory().post('/lti/')

        with self.assertRaises(LTINotInSessionException):
            request.session = {}
            lti.verify(request)

        request.session = {LTI_SESSION_KEY: True}
        self.assertTrue(lti.verify(request))
