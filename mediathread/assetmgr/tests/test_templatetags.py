from django.test.testcases import TestCase

from mediathread.assetmgr.models import Asset, Source
from mediathread.assetmgr.templatetags.assetlinks import InCourseNode
from mediathread.factories import MediathreadTestMixin


class MockNodeList(object):
    def __init__(self):
        self.rendered = False

    def render(self, c):
        self.rendered = True


class TestInCourse(MediathreadTestMixin, TestCase):

    def setUp(self):
        self.setup_sample_course()
        self.setup_alternate_course()

        self.archive = Asset.objects.create(title="Sample Archive",
                                            course=self.sample_course,
                                            author=self.instructor_one)
        primary = Source.objects.create(asset=self.archive,
                                        label='archive',
                                        primary=True,
                                        url="http://ccnmtl.columbia.edu")
        self.archive.source_set.add(primary)

    def test_not_in_course(self):
        nlTrue = MockNodeList()
        nlFalse = MockNodeList()

        node = InCourseNode('archive', 'course', nlTrue, nlFalse)
        context = dict(archive=self.archive, course=self.alt_course)
        out = node.render(context)
        self.assertEqual(out, None)
        self.assertFalse(nlTrue.rendered)
        self.assertTrue(nlFalse.rendered)

    def test_is_in_course(self):
        nlTrue = MockNodeList()
        nlFalse = MockNodeList()

        node = InCourseNode('archive', 'course', nlTrue, nlFalse)
        context = dict(archive=self.archive, course=self.sample_course)
        out = node.render(context)
        self.assertEqual(out, None)
        self.assertTrue(nlTrue.rendered)
        self.assertFalse(nlFalse.rendered)
