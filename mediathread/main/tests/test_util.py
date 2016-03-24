from django.core import mail
from django.test.testcases import TestCase

from mediathread.main.util import send_template_email


class SendTemplateEmailTest(TestCase):

    def test_send_template_email(self):
        with self.settings(SERVER_EMAIL='mediathread@example.com'):
            send_template_email('foo', 'main/contact_email_response.txt',
                                {'name': 'bar'}, 'abc123@columbia.edu')
            self.assertEqual(len(mail.outbox), 1)
            self.assertEqual(mail.outbox[0].subject, 'foo')
            self.assertEquals(mail.outbox[0].from_email,
                              'mediathread@example.com')
            self.assertTrue(mail.outbox[0].to, ['abc123@columbia.edu'])
