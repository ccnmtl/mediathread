from django.contrib.auth.models import User
from django.template.base import Template
from django.template.context import Context
from django.test.testcases import TestCase


class TestTemplateTags(TestCase):
    fixtures = ['unittest_sample_course.json']

    def test_user_courses(self):
        user = User.objects.get(username='test_instructor_two')
        out = Template(
            "{% load user_projects %}"
            "{% num_courses for user as user_courses %}"
            "{{user_courses}}"
        ).render(Context({'user': user}))
        self.assertEqual(out, "2")
