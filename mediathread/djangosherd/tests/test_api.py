from django.test.client import RequestFactory
from django.test.testcases import TestCase

from mediathread.djangosherd.api import DiscussionIndexResource
from mediathread.djangosherd.models import DiscussionIndex
from mediathread.factories import MediathreadTestMixin


class DiscussionIndexResourcesTest(MediathreadTestMixin, TestCase):

    def test_render(self):
        self.setup_sample_course()
        self.create_discussion(self.sample_course, self.instructor_one)

        indicies = DiscussionIndex.objects.all()

        request = RequestFactory().get('/')
        request.course = self.sample_course
        request.user = self.instructor_one
        ctx = DiscussionIndexResource().render_list(request, indicies)
        self.assertTrue('references' in ctx)
        self.assertEquals(ctx['references'][0]['title'],
                          'Sample Course Discussion')
        self.assertEquals(ctx['references'][0]['type'], 'discussion')
