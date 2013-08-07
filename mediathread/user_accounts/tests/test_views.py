from allauth.account.models import EmailAddress, EmailConfirmation
from customerio import CustomerIO
from django.test.utils import override_settings
from mock import patch, MagicMock

from django.conf import settings
from django.contrib.auth.models import User
from django.core import mail
from django.core.urlresolvers import reverse
from django.test import TestCase

from courseaffils.models import Course
from mediathread.user_accounts import autocomplete_light_registry
from mediathread.user_accounts import forms

mock_customerio = MagicMock(spec=CustomerIO)


@patch("customerio.CustomerIO", mock_customerio)
class InviteStudentsTest(TestCase):
    fixtures = ['unittest_sample_course.json']

    def setUp(self):
        self.client.login(username="test_instructor", password="test")
        course = Course.objects.get(pk=1)
        course.user_set.clear()
        session = self.client.session
        session['ccnmtl.courseaffils.course'] = course
        session.save()

    def test_page_shows_the_form(self):
        response = self.client.get(reverse("invite-students"))
        self.assertContains(response, "form", status_code=200)

    def test_invite_new_student(self):
        """
        Invite a student that does not have an existing user account
        """
        course = self.client.session['ccnmtl.courseaffils.course']
        response = self.client.post(reverse("invite-students"), {
            'email_from': 'test@instructor.com',
            'student_emails': 'test@student.com',
            'message': 'Welcome!'
        }, follow=True)
        self.assertEquals(User.objects.filter(email="test@student.com").count(), 1)
        self.assertEquals(course.user_set.filter(email="test@student.com").count(), 1)
        self.assertEqual(len(mail.outbox), 1)

    def test_invite_multiple_new_students(self):
        """
        Invite mulitple students that do not have an existing user account
        """
        course = self.client.session['ccnmtl.courseaffils.course']
        response = self.client.post(reverse("invite-students"), {
            'email_from': 'test@instructor.com',
            'student_emails': 'test@student.com' + '\n' +
                              'test2@student.com' + '\n' +
                              'test3@student.com',
            'message': 'Welcome!'
        }, follow=True)
        self.assertEquals(User.objects.filter(email__contains="@student.com").count(), 3)
        self.assertEquals(course.user_set.filter(email__contains="@student.com").count(), 3)
        self.assertEqual(len(mail.outbox), 3)

    def test_invite_existing_student(self):
        course = self.client.session['ccnmtl.courseaffils.course']
        test_student = User.objects.get(username="test_student_one")
        test_student.email = "test_student_one@example.com"
        test_student.save()
        response = self.client.post(reverse("invite-students"), {
            'email_from': 'test@instructor.com',
            'student_emails': 'test_student_one@example.com',
            'message': 'Welcome!'
        }, follow=True)
        self.assertEquals(User.objects.filter(email="test_student_one@example.com").count(), 1)
        self.assertEquals(course.user_set.filter(email="test_student_one@example.com").count(), 1)
        self.assertEqual(len(mail.outbox), 0)
        self.assertTrue(mock_customerio.called)

    def test_invite_multiple_existing_students(self):
        course = self.client.session['ccnmtl.courseaffils.course']
        for s in User.objects.filter(username__contains="test_student"):
            s.email = "{0}@example.com".format(s.username)
            s.save()
        response = self.client.post(reverse("invite-students"), {
            'email_from': 'test@instructor.com',
            'student_emails': 'test_student_one@example.com' + '\n' +
                              'test_student_two@example.com' + '\n' +
                              'test_student_three@example.com' + '\n' +
                              'test_student_alt@example.com',
            'message': 'Welcome!'
        }, follow=True)
        self.assertEquals(User.objects.filter(email__contains="@example.com").count(), 4)
        self.assertEquals(course.user_set.filter(email__contains="@example.com").count(), 4)
        self.assertEqual(len(mail.outbox), 0)
        self.assertTrue(mock_customerio.called)

    def test_redirect_unregistered_users(self):
        self.client.logout()
        response = self.client.get(reverse("invite-students"))
        self.assertRedirects(response, reverse("account_login") + '?next=' + reverse("invite-students"))

    def test_incorrect_email_address(self):
        response = self.client.post(reverse("invite-students"), {
            'email_from': 'test@instructor.com',
            'student_emails': 'wrongemail.com',
            'message': 'Welcome!'
        }, follow=True)
        self.assertFormError(response, 'form', 'student_emails', 'Error in an email address')

    def test_missing_form_fields(self):
        response = self.client.post(reverse("invite-students"), {
            'email_from': '',
            'student_emails': '',
            'message': ''
        }, follow=True)
        self.assertFormError(response, 'form', 'email_from', 'This field is required.')
        self.assertFormError(response, 'form', 'student_emails', 'This field is required.')
        self.assertFormError(response, 'form', 'message', 'This field is required.')


class RegistrationTest(TestCase):
    fixtures = ['unittest_sample_course.json']

    def setUp(self):
        self.post_params = {
            'email': 'testmediathread@appsembler.com',
            'password': 'testpassword',
            'first_name': 'Appsembler',
            'last_name': 'Rocks',
            'position_title': 'professor',
            'hear_mediathread_from': 'conference',
            'subscribe_to_newsletter': 'on',
            'agree_to_term': 'on',
            'organization': 'TestCompany Inc.'
        }

    def test_registration_get(self):
        response = self.client.get(reverse("registration-form"))
        self.assertTrue(response.context['form'])
        self.assertEqual(response.status_code, 200)

    @override_settings(SAMPLE_COURSE_ID=1)
    def test_registration_post(self):
        response = self.client.post(reverse("registration-form"), self.post_params)
        self.assertEqual(response.status_code, 200)
        self.assertEquals(User.objects.filter(email="testmediathread@appsembler.com").count(), 1)
        user = User.objects.get(email="testmediathread@appsembler.com")
        self.assertEquals(user.get_full_name(), "Appsembler Rocks")
        self.assertEqual(len(mail.outbox), 1)
        self.assertEquals(EmailConfirmation.objects.filter(email_address__email="testmediathread@appsembler.com").count(), 1)
        self.assertEquals(EmailAddress.objects.filter(email="testmediathread@appsembler.com", verified=False).count(), 1)
        sample_course = Course.objects.get(id=settings.SAMPLE_COURSE_ID)
        self.assertTrue(user.id in sample_course.group.user_set.values_list('id', flat=True))
