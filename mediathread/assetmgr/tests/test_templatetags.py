from courseaffils.models import Course
from django.contrib.auth.models import User
from django.test.testcases import TestCase
from mediathread.assetmgr.models import Asset, Source
from mediathread.assetmgr.templatetags.assetlinks import InCourseNode


class MockNodeList(object):
    def __init__(self):
        self.rendered = False

    def render(self, c):
        self.rendered = True


class TestInCourse(TestCase):
    fixtures = ['unittest_sample_course.json']

    def setUp(self):
        self.user = User.objects.get(username='test_instructor')
        self.course = Course.objects.get(title='Sample Course')
        self.archive = Asset.objects.create(title="Sample Archive",
                                            course=self.course,
                                            author=self.user)
        primary = Source.objects.create(asset=self.archive, label='archive',
                                        primary=True,
                                        url="http://ccnmtl.columbia.edu")
        self.archive.source_set.add(primary)

        self.alt_course = Course.objects.get(title='Alternate Course')

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
        context = dict(archive=self.archive, course=self.course)
        out = node.render(context)
        self.assertEqual(out, None)
        self.assertTrue(nlTrue.rendered)
        self.assertFalse(nlFalse.rendered)
