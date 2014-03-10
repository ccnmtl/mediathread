from courseaffils.models import Course
from django.test.testcases import TestCase
from mediathread.projects.models import Project
from structuredcollaboration.models import Collaboration


class ModelsTest(TestCase):
    # Use ``fixtures`` & ``urls`` as normal. See Django's ``TestCase``
    # documentation for the gory details.
    fixtures = ['unittest_sample_course.json',
                'unittest_sample_projects.json']

    def test_get_associated_collaboration_project(self):
        project = Project.objects.get(id=2)
        collaboration = Collaboration.get_associated_collab(project)
        self.assertIsNotNone(collaboration)

    def test_get_associated_collaboration_course(self):
        course = Course.objects.get(id=2)
        collaboration = Collaboration.get_associated_collab(course)
        self.assertIsNotNone(collaboration)
