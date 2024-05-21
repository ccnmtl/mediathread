from django.test.testcases import TestCase

from mediathread.assetmgr.templatetags.assetlinks import map_course_collection
from mediathread.factories import MediathreadTestMixin, \
    SuggestedExternalCollectionFactory, ExternalCollectionFactory


class TestInCourse(MediathreadTestMixin, TestCase):

    def setUp(self):
        self.setup_sample_course()
        self.setup_alternate_course()

        self.suggested = SuggestedExternalCollectionFactory(title="Sample")
        self.collection = ExternalCollectionFactory(course=self.sample_course,
                                                    title="Sample")

    def test_not_in_course(self):
        self.assertIsNone(map_course_collection(self.alt_course,
                                                self.suggested))

    def test_is_in_course(self):
        self.assertEqual(
            map_course_collection(self.sample_course, self.suggested),
            self.collection)
