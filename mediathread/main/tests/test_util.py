from django.core import mail
from django.test.testcases import TestCase
from courseaffils.tests.factories import AffilFactory

from mediathread.factories import UserFactory
from mediathread.main.util import (
    send_template_email, user_display_name, course_exists
)


class UtilTest(TestCase):

    def test_send_template_email(self):
        with self.settings(SERVER_EMAIL='mediathread@example.com'):
            send_template_email('foo', 'main/contact_email_response.txt',
                                {'name': 'bar'}, 'abc123@columbia.edu')
            self.assertEqual(len(mail.outbox), 1)
            self.assertEqual(mail.outbox[0].subject, 'foo')
            self.assertEquals(mail.outbox[0].from_email,
                              'mediathread@example.com')
            self.assertTrue(mail.outbox[0].to, ['abc123@columbia.edu'])

    def test_user_display_name(self):
        user = UserFactory()
        self.assertEquals(user_display_name(user), user.username)

        user = UserFactory(first_name='John', last_name='Smith')
        self.assertEquals(user_display_name(user), 'John Smith')

    def test_course_exists(self):
        a = AffilFactory()
        self.assertIsNone(course_exists(a))
