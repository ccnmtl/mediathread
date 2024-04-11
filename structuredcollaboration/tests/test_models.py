from django.test.testcases import TestCase

from mediathread.factories import MediathreadTestMixin, ProjectFactory
from structuredcollaboration.models import Collaboration


class ModelsTest(MediathreadTestMixin, TestCase):

    def setUp(self):
        self.setup_sample_course()

    def test_get_associated_collaboration_project(self):
        project = ProjectFactory.create(
            course=self.sample_course, author=self.student_one,
            policy='PrivateEditorsAreOwners')
        collaboration = Collaboration.objects.get_for_object(project)
        self.assertIsNotNone(collaboration)

    def test_get_associated_collaboration_course(self):
        collaboration = Collaboration.objects.get_for_object(
            self.sample_course)
        self.assertIsNotNone(collaboration)

    def test_append_remove_child(self):
        parent = ProjectFactory.create(
            course=self.sample_course, author=self.instructor_one,
            policy='CourseProtected', project_type='assignment')

        response = ProjectFactory.create(
            course=self.sample_course, author=self.student_one,
            policy='PrivateEditorsAreOwners')

        parent.get_collaboration().append_child(response)

        collaboration = response.get_collaboration()
        self.assertEqual(collaboration.get_parent().content_object, parent)

        parent.get_collaboration().remove_children()
        collaboration.refresh_from_db()
        self.assertIsNone(collaboration.get_parent())
