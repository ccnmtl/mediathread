from django.test.client import RequestFactory
from django.test.testcases import TestCase

from mediathread.djangosherd.permissions import AssetIsVisible
from mediathread.factories import MediathreadTestMixin, AssetFactory


class AssetIsVisibleTest(MediathreadTestMixin, TestCase):

    def test_has_object_permission(self):
        perm = AssetIsVisible()

        request = RequestFactory().get('/')

        student_item = AssetFactory(
            title='One', primary_source='image', author=self.student_one)

        request.user = self.student_one
        self.assertTrue(
            perm.has_object_permission(request, None, student_item))

        request.user = self.student_two
        self.assertFalse(
            perm.has_object_permission(request, None, student_item))

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
