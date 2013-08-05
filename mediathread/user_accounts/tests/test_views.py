from django.core import mail
from mock import patch, MagicMock
from django.test import TestCase
from customerio import CustomerIO
from courseaffils.models import Course
from django.contrib.auth.models import User

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
        response = self.client.get("/user_accounts/invite_students/")
        self.assertContains(response, "form", status_code=200)

    def test_invite_new_student(self):
        """
        Invite a student that does not have an existing user account
        """
        course = self.client.session['ccnmtl.courseaffils.course']
        response = self.client.post("/user_accounts/invite_students/", {
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
        response = self.client.post("/user_accounts/invite_students/", {
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
        response = self.client.post("/user_accounts/invite_students/", {
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
        response = self.client.post("/user_accounts/invite_students/", {
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
        response = self.client.get("/user_accounts/invite_students/")
        self.assertRedirects(response, '/accounts/login/?next=/user_accounts/invite_students/')
