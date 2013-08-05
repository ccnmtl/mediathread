from courseaffils.models import Course
from django.test import TestCase


class CourseCreateTest(TestCase):
    fixtures = ['unittest_sample_course.json']

    def setUp(self):
        self.client.login(username="test_instructor", password="test")

    def test_page_shows_the_form(self):
        response = self.client.get("/user_accounts/invite_students/")
        self.assertContains(response, "form", status_code=200)

    def test_create_first_course(self):
        response = self.client.post("/course/create/", {
            'title': "Sample course #1",
            'organization': "Test organization",
            'student_amount': '10'
        })
        self.assertRedirects(response, '/')
        self.assertTrue(Course.objects.filter(title="Sample course #1").exists())
        course = Course.objects.get(title="Sample course #1")
        self.assertTrue("test_instructor" in course.faculty_group.user_set.values_list('username', flat=True))
        self.assertTrue("test_instructor" in course.user_set.values_list('username', flat=True))

    def test_missing_form_fields(self):
        response = self.client.post("/course/create/", {
            'title': "",
            'organization': "",
            'student_amount': '10'
        })
        self.assertFormError(response, 'form', 'title', 'This field is required.')
        self.assertFormError(response, 'form', 'organization', 'This field is required.')
