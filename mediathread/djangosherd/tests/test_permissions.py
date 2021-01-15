from django.core.exceptions import PermissionDenied
from django.test.client import RequestFactory
from django.test.testcases import TestCase
from mediathread.djangosherd.permissions import AssetIsVisible
from mediathread.factories import MediathreadTestMixin, AssetFactory
from mediathread.main.course_details import ITEM_VISIBILITY_KEY


class AssetIsVisibleTest(MediathreadTestMixin, TestCase):

    def test_has_object_permission(self):
        self.setup_sample_course()

        perm = AssetIsVisible()

        request = RequestFactory().get('/')

        student_item = AssetFactory(
            course=self.sample_course,
            title='One', primary_source='image',
            author=self.student_one)

        request.user = self.student_one
        self.assertTrue(
            perm.has_object_permission(request, None, student_item))

        request.user = self.student_two
        self.assertTrue(
            perm.has_object_permission(request, None, student_item))

        self.sample_course.add_detail(ITEM_VISIBILITY_KEY, 0)
        request.user = self.student_two
        with self.assertRaises(PermissionDenied):
            perm.has_object_permission(request, None, student_item)

        request.user = self.instructor_one
        self.assertTrue(
            perm.has_object_permission(request, None, student_item))

        instructor_item = AssetFactory(
            title='Two', primary_source='image', author=self.instructor_one)
        request.user = self.student_one
        self.assertTrue(
            perm.has_object_permission(request, None, instructor_item))

        request.user = self.instructor_one
        self.assertTrue(
            perm.has_object_permission(request, None, instructor_item))
