from courseaffils.models import Course
from django.contrib.contenttypes.models import ContentType
from django.test.client import RequestFactory
from django.test.testcases import TestCase

from mediathread.discussions.utils import get_course_discussions
from mediathread.discussions.views import discussion_delete, discussion_view
from mediathread.factories import MediathreadTestMixin
from structuredcollaboration.models import Collaboration


class DiscussionViewsTest(MediathreadTestMixin, TestCase):

    def test_create_discussions(self):
        self.setup_sample_course()
        self.setup_alternate_course()

        self.create_discussion(self.sample_course, self.instructor_one)
        self.create_discussion(self.alt_course, self.alt_instructor)

        discussions = get_course_discussions(self.sample_course)
        self.assertEquals(1, len(discussions))
        self.assertEquals(discussions[0].title, "Sample Course Discussion")

        discussions = get_course_discussions(self.alt_course)
        self.assertEquals(1, len(discussions))
        self.assertEquals(discussions[0].title, "Alternate Course Discussion")

    def test_delete_discussions(self):
        self.setup_sample_course()
        self.create_discussion(self.sample_course, self.instructor_one)
        discussions = get_course_discussions(self.sample_course)
        self.assertEquals(1, len(discussions))

        request = RequestFactory().post('/discussion/delete/', {})
        request.user = self.instructor_one
        request.course = self.sample_course
        request.collaboration_context, created = \
            Collaboration.objects.get_or_create(
                content_type=ContentType.objects.get_for_model(Course),
                object_pk=str(self.sample_course.pk))

        discussion_delete(request, discussions[0].id)
        discussions = get_course_discussions(self.sample_course)
        self.assertEquals(0, len(discussions))

    def test_view_discussions(self):
        self.setup_sample_course()
        self.create_discussion(self.sample_course, self.instructor_one)
        discussions = get_course_discussions(self.sample_course)
        self.assertEquals(1, len(discussions))

        request = RequestFactory().get('/discussion/delete/', {})
        request.user = self.instructor_one
        request.course = self.sample_course
        request.collaboration_context, created = \
            Collaboration.objects.get_or_create(
                content_type=ContentType.objects.get_for_model(Course),
                object_pk=str(self.sample_course.pk))

        discussions = get_course_discussions(self.sample_course)
        response = discussion_view(request, discussions[0].id)
        self.assertEquals(response.status_code, 200)

    def test_view_discussions_ajax(self):
        self.setup_sample_course()
        self.create_discussion(self.sample_course, self.instructor_one)
        discussions = get_course_discussions(self.sample_course)
        self.assertEquals(1, len(discussions))

        request = RequestFactory().get('/discussion/delete/', {},
                                       )
        request.user = self.instructor_one
        request.course = self.sample_course
        request.collaboration_context, created = \
            Collaboration.objects.get_or_create(
                content_type=ContentType.objects.get_for_model(Course),
                object_pk=str(self.sample_course.pk))

        discussions = get_course_discussions(self.sample_course)
        response = discussion_view(request, discussions[0].id)
        self.assertEquals(response.status_code, 200)
