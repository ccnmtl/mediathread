from datetime import datetime

from django.template.base import Template
from django.template.context import Context
from django.test import TestCase, RequestFactory
from django.urls import reverse
from django_comments.forms import CommentSecurityForm
from mediathread.factories import UserFactory, MediathreadTestMixin, \
    ProjectFactory
from mediathread.projects.models import PUBLISH_WHOLE_CLASS, PUBLISH_DRAFT, \
    Project
from mediathread.projects.templatetags.user_projects import (
    published_assignment_responses, comment_count, my_assignment_responses,
    assignment_responses)


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

    def test_assignment_response_tags(self):
        assignment = ProjectFactory.create(
            course=self.sample_course, author=self.instructor_one,
            policy=PUBLISH_WHOLE_CLASS[0], project_type='assignment')

        visible_response = ProjectFactory.create(
            course=self.sample_course, author=self.student_one,
            policy=PUBLISH_WHOLE_CLASS[0], parent=assignment,
            date_submitted=datetime.today())

        draft_response = ProjectFactory.create(
            course=self.sample_course, author=self.student_two,
            policy=PUBLISH_DRAFT[0], parent=assignment,
            date_submitted=datetime.today())

        request = RequestFactory().get('/')
        request.course = self.sample_course
        request.user = self.student_one
        responses = assignment_responses(assignment, request)
        self.assertEqual(len(responses), 1)
        self.assertEqual(responses[0], visible_response)

        self.assertEquals(published_assignment_responses(assignment), 1)

        responses = my_assignment_responses(assignment, self.student_two)
        self.assertEqual(responses.count(), 1)
        self.assertEqual(responses.first().content_object, draft_response)

        responses = my_assignment_responses(assignment, self.student_one)
        self.assertEqual(responses.count(), 1)
        self.assertEqual(responses.first().content_object, visible_response)

    def _add_comment(self, discussion, author):
        url = reverse('comments-post-comment')
        data = {
            u'comment': [u'posted'],
            u'parent': [discussion.id],  # threadedcomment
            u'name': [],
            u'title': [u''],
            u'url': [u'']
        }

        frm = CommentSecurityForm(target_object=discussion.content_object)
        data.update(frm.generate_security_data())

        self.client.login(username=author.username, password='test')
        self.switch_course(self.client, self.sample_course)
        response = self.client.post(url, data)
        self.assertEquals(response.status_code, 302)

    def test_discussion_assignment_response_tags(self):
        self.client.login(username=self.instructor_one.username,
                          password='test')
        data = {
            u'body': [u'<p>Talk</p>'],
            u'project_type': [u'discussion-assignment'],
            u'publish': [u'CourseProtected'],
            u'title': [u'Important Discussion']}
        url = reverse('discussion-assignment-create',
                      args=[self.sample_course.id])
        response = self.client.post(url, data, follow=True)
        self.assertEqual(response.status_code, 200)
        assignment = Project.objects.get(title='Important Discussion')
        self.assertEquals(published_assignment_responses(assignment), 0)
        self.assertEqual(
            comment_count(assignment, self.instructor_one)[0], 1)
        self.assertEqual(
            comment_count(assignment, self.instructor_two)[0], 0)
        self.assertEqual(
            comment_count(assignment, self.student_one)[0], 0)

        # add a comment
        discussion = assignment.course_discussion()
        self._add_comment(discussion, self.instructor_two)
        self.assertEquals(published_assignment_responses(assignment), 0)
        self._add_comment(discussion, self.student_one)
        self.assertEquals(published_assignment_responses(assignment), 1)

        self.assertEqual(
            comment_count(assignment, self.instructor_two)[0], 1)
        self.assertEqual(
            comment_count(assignment, self.student_one)[0], 1)
