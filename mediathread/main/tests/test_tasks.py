from django.conf import settings
from django.contrib.messages.api import get_messages
from django.contrib.messages.constants import ERROR, INFO
from django.contrib.messages.storage.fallback import FallbackStorage
from django.core import mail
from django.core.cache import cache
from django.test import TestCase
from django.test.client import RequestFactory
from mediathread.factories import MediathreadTestMixin, AssetFactory, \
    CourseFactory
from mediathread.main.models import PanoptoIngestLogEntry
from mediathread.main.tasks import PanoptoIngester


class PanoptoIngesterTest(MediathreadTestMixin, TestCase):

    def setUp(self):
        self.setup_sample_course()

        self.request = RequestFactory().get('/')
        self.request.course = self.sample_course

        setattr(self.request, 'session', 'session')
        messages = FallbackStorage(self.request)
        setattr(self.request, '_messages', messages)

        self.ingester = PanoptoIngester(self.request)

    def tearDown(self):
        cache.clear()

    def test_log_message(self):
        self.ingester.log_message(
            self.sample_course, {'Id': 4}, ERROR, 'logged')

        messages = [m.message for m in get_messages(self.request)]
        self.assertTrue('logged' in messages)

        # if not request is passed, the log entries go to the database
        ingester = PanoptoIngester()
        ingester.log_message(self.sample_course, {'Id': 4}, INFO, 'foo')
        messages = [m.message for m in get_messages(self.request)]
        self.assertFalse('foo' in messages)

        log_entry = PanoptoIngestLogEntry.objects.first()
        self.assertIsNotNone(log_entry)
        self.assertEqual(log_entry.session_id, '4')
        self.assertEqual(log_entry.course, self.sample_course)
        self.assertEqual(log_entry.level, INFO)
        self.assertEqual(log_entry.message, 'foo')

    def test_is_already_imported(self):
        session = {'Name': 'The Name', 'Id': 'source url'}
        self.assertFalse(self.ingester.is_already_imported(
            self.sample_course, session))
        AssetFactory(course=self.sample_course,
                     author=self.student_one,
                     primary_source='mp4_panopto')
        self.assertTrue(self.ingester.is_already_imported(
            self.sample_course, session))

    def test_get_author(self):
        self.assertEqual(
            self.ingester.get_author(self.sample_course, 'student_one'),
            (self.student_one, False))

        user, created = self.ingester.get_author(self.sample_course, 'zz123')
        self.assertTrue(self.sample_course.is_true_member(user))

    def test_create_item(self):
        with self.settings(PANOPTO_SERVER='localhost/'):
            item = self.ingester.create_item(
                self.sample_course,
                'Doe, Jim', self.student_one, 'session_id', 'thumb')

            self.assertTrue(item.title, 'Doe, Jim')
            self.assertEqual(item.course, self.sample_course)
            self.assertEqual(item.author, self.student_one)
            self.assertEqual(item.primary.url, 'session_id')
            self.assertEqual(item.thumb_url, 'https://localhost/thumb')
            self.assertEqual(item.primary.label, 'mp4_panopto')

    def test_complete_incomplete(self):
        ctx = {'State': 'foo', 'Name': 'bar', 'Id': 1}
        self.assertFalse(self.ingester.is_session_complete(
            self.sample_course, ctx))
        messages = [m.message for m in get_messages(self.request)]
        self.assertTrue('bar (1) incomplete' in messages)

    def test_complete_icomplete(self):
        ctx = {'State': 'Complete', 'Name': 'bar', 'Id': 1}
        self.assertTrue(self.ingester.is_session_complete(
            self.sample_course, ctx))
        messages = [m.message for m in get_messages(self.request)]
        self.assertEqual(len(messages), 0)

    def test_add_session_status(self):
        item = AssetFactory(
            id=1, title='Item',
            course=self.sample_course, author=self.student_one,
            primary_source='mp4_panopto')

        session = {'Name': 'bar', 'Id': 1}
        self.ingester.add_session_status(
            self.sample_course, session, item, self.student_one, False)
        messages = [m.message for m in get_messages(self.request)]
        self.assertTrue(
            'bar (1) saved as <a href="/asset/1/">Item</a> for Student One' in
            messages)

        session = {'Name': 'bar', 'Id': 1}
        self.ingester.add_session_status(
            self.sample_course, session, item, self.student_one, True)
        messages = [m.message for m in get_messages(self.request)]
        self.assertTrue(
            ('bar (1) saved as <a href="/asset/1/">Item</a>'
             ' for Student One. <b>student_one is a new user</b>') in messages)

    def test_send_email(self):
        item = AssetFactory(
            id=1, title='Item',
            course=self.sample_course, author=self.student_one,
            primary_source='mp4_panopto')

        self.ingester.send_email(self.sample_course, self.student_one, item)

        self.assertEqual(len(mail.outbox), 1)

        self.assertEqual(mail.outbox[0].subject,
                         'Mediathread submission now available')
        self.assertEqual(mail.outbox[0].from_email, settings.SERVER_EMAIL)
        self.assertEqual(mail.outbox[0].to, [self.student_one.email])

    def test_parse_description(self):
        a = self.ingester.parse_description(
            {'Id': 1, 'Name': 'session1', 'Description': ''})
        self.assertEqual(a, [])
        msgs = [m.message for m in get_messages(self.request)]
        self.assertTrue(
            ('session1 (1) does not have a UNI and/or coursestring') in msgs)

        a = self.ingester.parse_description(
            {'Id': 1, 'Name': 'session1', 'Description': 'foo'})
        self.assertEqual(a, [])

        a = self.ingester.parse_description(
            {'Id': 1, 'Name': 'session1', 'Description': 'uni,course'})
        self.assertEqual(a, ['uni', 'course'])

    def test_get_course(self):
        session = {'Id': 1, 'Name': 'session1'}
        course_string = 'SOCWT7100_099_2020_3'
        self.assertIsNone(self.ingester.get_course(session, course_string))

        msgs = [m.message for m in get_messages(self.request)]
        self.assertTrue(
            ('session1 (1): No course matches SOCWT7100_099_2020_3') in msgs)

        course = CourseFactory()
        course.group.name = 't1.y2010.s001.cf1000.scnc.st.course:columbia.edu'
        course.group.save()
        course_string = 'SCNCF1000_001_2010_1'
        self.assertEqual(
            self.ingester.get_course(session, course_string),
            course)
