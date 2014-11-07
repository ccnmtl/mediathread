from django.template.base import Template
from django.template.context import Context
from django.test.testcases import TestCase

from mediathread.factories import UserFactory, MediathreadTestMixin


class TestTemplateTags(MediathreadTestMixin, TestCase):

    def setUp(self):
        self.setup_sample_course()
        self.setup_alternate_course()

    def test_user_courses(self):

        # instructor that sees both Sample Course & Alternate Course
        self.instructor_three = UserFactory(username='instructor_three')
        self.add_as_faculty(self.sample_course, self.instructor_three)
        self.add_as_faculty(self.alt_course, self.instructor_three)

        out = Template(
            "{% load user_projects %}"
            "{% num_courses for user as user_courses %}"
            "{{user_courses}}"
        ).render(Context({'user': self.instructor_three}))
        self.assertEqual(out, "2")
