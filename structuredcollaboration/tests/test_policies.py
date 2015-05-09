from django.test.client import RequestFactory
from django.test.testcases import TestCase

from mediathread.discussions.utils import get_course_discussions
from mediathread.factories import CollaborationFactory, UserFactory, \
    MediathreadTestMixin, ProjectFactory
from structuredcollaboration.models import Collaboration
from structuredcollaboration.policies import PublicEditorsAreOwners, \
    PrivateEditorsAreOwners, CollaborationPolicy, \
    PrivateStudentAndFaculty, InstructorShared, InstructorManaged, \
    CourseProtected, Assignment


class PoliciesTest(MediathreadTestMixin, TestCase):

    def setUp(self):
        self.setup_sample_course()
        self.setup_alternate_course()

    def test_forbidden(self):
        policy = CollaborationPolicy()
        collaboration = CollaborationFactory()

        request = RequestFactory().get('/')

        request.user = collaboration.user
        self.assertFalse(policy.permission_to(
            collaboration, 'read', request))
        self.assertFalse(policy.permission_to(
            collaboration, 'edit', request))
        self.assertFalse(policy.permission_to(
            collaboration, 'manage', request))
        self.assertFalse(policy.permission_to(
            collaboration, 'delete', request))

    def test_public_editors_are_owners(self):
        policy = PublicEditorsAreOwners()
        collaboration = CollaborationFactory()

        request = RequestFactory().get('/')

        request.user = collaboration.user
        self.assertTrue(policy.read(collaboration, request))
        self.assertTrue(policy.edit(collaboration, request))
        self.assertTrue(policy.manage(collaboration, request))
        self.assertTrue(policy.delete(collaboration, request))

        request.user = UserFactory()  # random user
        self.assertTrue(policy.read(collaboration, request))
        self.assertFalse(policy.edit(collaboration, request))
        self.assertFalse(policy.manage(
            collaboration, request))
        self.assertFalse(policy.delete(
            collaboration, request))

        collaboration.group.user_set.add(request.user)  # now a group member
        self.assertTrue(policy.read(collaboration, request))
        self.assertTrue(policy.edit(collaboration, request))
        self.assertTrue(policy.manage(collaboration, request))
        self.assertTrue(policy.delete(collaboration, request))

    def test_private_editors_are_owners(self):
        policy = PrivateEditorsAreOwners()
        collaboration = CollaborationFactory()

        request = RequestFactory().get('/')

        request.user = collaboration.user
        self.assertTrue(policy.read(collaboration, request))
        self.assertTrue(policy.edit(collaboration, request))
        self.assertTrue(policy.manage(collaboration, request))
        self.assertTrue(policy.delete(collaboration, request))

        request.user = UserFactory()  # random user
        self.assertFalse(policy.read(collaboration, request))
        self.assertFalse(policy.edit(collaboration, request))
        self.assertFalse(policy.manage(
            collaboration, request))
        self.assertFalse(policy.delete(
            collaboration, request))

        collaboration.group.user_set.add(request.user)  # now a group member
        self.assertTrue(policy.read(collaboration, request))
        self.assertTrue(policy.edit(collaboration, request))
        self.assertTrue(policy.manage(collaboration, request))
        self.assertTrue(policy.delete(collaboration, request))

        request.user = UserFactory(is_staff=True)
        self.assertTrue(policy.read(collaboration, request))
        self.assertFalse(policy.edit(collaboration, request))
        self.assertFalse(policy.manage(
            collaboration, request))
        self.assertFalse(policy.delete(
            collaboration, request))

    def test_private_student_faculty(self):
        policy = PrivateStudentAndFaculty()

        request = RequestFactory().get('/')
        collaboration = Collaboration.objects.get_for_object(
            self.sample_course)
        request.course = self.sample_course
        request.collaboration_context = collaboration

        self.create_discussion(self.sample_course, self.instructor_one)
        discussions = get_course_discussions(self.sample_course)
        collaboration = Collaboration.objects.get_for_object(discussions[0])

        request.user = self.student_one
        self.assertFalse(policy.read(collaboration, request))
        self.assertFalse(policy.edit(collaboration, request))
        self.assertFalse(policy.manage(collaboration, request))
        self.assertFalse(policy.delete(collaboration, request))

        request.user = self.instructor_one
        self.assertTrue(policy.read(collaboration, request))
        self.assertTrue(policy.edit(collaboration, request))
        self.assertTrue(policy.manage(collaboration, request))
        self.assertTrue(policy.delete(collaboration, request))

        request.user = self.student_two
        self.assertFalse(policy.read(collaboration, request))
        self.assertFalse(policy.edit(collaboration, request))
        self.assertFalse(policy.manage(collaboration, request))
        self.assertFalse(policy.delete(collaboration, request))

    def test_instructor_shared(self):
        policy = InstructorShared()

        request = RequestFactory().get('/')
        collaboration = Collaboration.objects.get_for_object(
            self.sample_course)
        request.course = self.sample_course
        request.collaboration_context = collaboration

        project = ProjectFactory.create(
            course=self.sample_course, author=self.student_one,
            policy='InstructorShared')
        collaboration = Collaboration.objects.get_for_object(project)

        request.user = self.student_one
        self.assertTrue(policy.read(collaboration, request))
        self.assertTrue(policy.edit(collaboration, request))
        self.assertTrue(policy.manage(collaboration, request))
        self.assertTrue(policy.delete(collaboration, request))

        request.user = self.student_two
        self.assertFalse(policy.read(collaboration, request))
        self.assertFalse(policy.edit(collaboration, request))
        self.assertFalse(policy.manage(collaboration, request))
        self.assertFalse(policy.delete(collaboration, request))

        request.user = self.instructor_one
        self.assertTrue(policy.read(collaboration, request))
        self.assertFalse(policy.edit(collaboration, request))
        self.assertFalse(policy.manage(collaboration, request))
        self.assertFalse(policy.delete(collaboration, request))

    def test_instructor_managed(self):
        policy = InstructorManaged()
        request = RequestFactory().get('/')
        request.course = self.sample_course
        request.collaboration_context = \
            Collaboration.objects.get_for_object(self.sample_course)

        project = ProjectFactory.create(
            course=self.sample_course, author=self.student_one,
            policy='InstructorShared')
        collaboration = Collaboration.objects.get_for_object(project)

        request.user = self.student_one
        self.assertTrue(policy.read(collaboration, request))
        self.assertTrue(policy.edit(collaboration, request))
        self.assertTrue(policy.manage(collaboration, request))
        self.assertTrue(policy.delete(collaboration, request))

        request.user = self.student_two
        self.assertTrue(policy.read(collaboration, request))
        self.assertTrue(policy.edit(collaboration, request))
        self.assertFalse(policy.manage(collaboration, request))
        self.assertFalse(policy.delete(collaboration, request))

        request.user = self.instructor_one
        self.assertTrue(policy.read(collaboration, request))
        self.assertTrue(policy.edit(collaboration, request))
        self.assertTrue(policy.manage(collaboration, request))
        self.assertTrue(policy.delete(collaboration, request))

        request.course = self.alt_course
        request.collaboration_context = \
            Collaboration.objects.get_for_object(self.alt_course)

        request.user = self.alt_instructor
        self.assertFalse(policy.read(collaboration, request))
        self.assertFalse(policy.edit(collaboration, request))
        self.assertFalse(policy.manage(collaboration, request))
        self.assertFalse(policy.delete(collaboration, request))

        request.user = self.alt_student
        self.assertFalse(policy.read(collaboration, request))
        self.assertFalse(policy.edit(collaboration, request))
        self.assertFalse(policy.manage(collaboration, request))
        self.assertFalse(policy.delete(collaboration, request))

    def test_course_protected(self):
        policy = CourseProtected()
        request = RequestFactory().get('/')

        collaboration = Collaboration.objects.get_for_object(
            self.sample_course)
        request.course = self.sample_course
        request.collaboration_context = collaboration

        project = ProjectFactory.create(
            course=self.sample_course, author=self.student_one,
            policy='CourseProtected')
        collaboration = Collaboration.objects.get_for_object(project)

        request.user = self.student_one
        self.assertTrue(policy.read(collaboration, request))
        self.assertTrue(policy.edit(collaboration, request))
        self.assertTrue(policy.manage(collaboration, request))
        self.assertTrue(policy.delete(collaboration, request))

        request.user = self.student_two
        self.assertTrue(policy.read(collaboration, request))
        self.assertFalse(policy.edit(collaboration, request))
        self.assertFalse(policy.manage(collaboration, request))
        self.assertFalse(policy.delete(collaboration, request))

        request.user = self.instructor_one
        self.assertTrue(policy.read(collaboration, request))
        self.assertFalse(policy.edit(collaboration, request))
        self.assertFalse(policy.manage(collaboration, request))
        self.assertFalse(policy.delete(collaboration, request))

    def test_assignment(self):
        policy = Assignment()

        request = RequestFactory().get('/')
        collaboration = Collaboration.objects.get_for_object(
            self.sample_course)
        request.course = self.sample_course
        request.collaboration_context = collaboration

        assignment = ProjectFactory.create(
            course=self.sample_course, author=self.instructor_one,
            policy='Assignment')
        collaboration = Collaboration.objects.get_for_object(assignment)

        request.user = self.student_one
        self.assertTrue(policy.read(collaboration, request))
        self.assertFalse(policy.edit(collaboration, request))
        self.assertFalse(policy.manage(collaboration, request))
        self.assertFalse(policy.delete(collaboration, request))

        request.user = self.instructor_one
        self.assertTrue(policy.read(collaboration, request))
        self.assertTrue(policy.edit(collaboration, request))
        self.assertTrue(policy.manage(collaboration, request))
        self.assertTrue(policy.delete(collaboration, request))
