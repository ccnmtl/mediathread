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
        course = None

        user = collaboration.user
        self.assertFalse(policy.permission_to(
            collaboration, 'read', course, user))
        self.assertFalse(policy.permission_to(
            collaboration, 'edit', course, user))
        self.assertFalse(policy.permission_to(
            collaboration, 'manage', course, user))
        self.assertFalse(policy.permission_to(
            collaboration, 'delete', course, user))

    def test_public_editors_are_owners(self):
        policy = PublicEditorsAreOwners()
        collaboration = CollaborationFactory()
        course = None

        user = collaboration.user
        self.assertTrue(policy.read(collaboration, course, user))
        self.assertTrue(policy.edit(collaboration, course, user))
        self.assertTrue(policy.manage(collaboration, course, user))
        self.assertTrue(policy.delete(collaboration, course, user))

        user = UserFactory()  # random user
        self.assertTrue(policy.read(collaboration, course, user))
        self.assertFalse(policy.edit(collaboration, course, user))
        self.assertFalse(policy.manage(
            collaboration, course, user))
        self.assertFalse(policy.delete(
            collaboration, course, user))

        collaboration.group.user_set.add(user)  # now a group member
        self.assertTrue(policy.read(collaboration, course, user))
        self.assertTrue(policy.edit(collaboration, course, user))
        self.assertTrue(policy.manage(collaboration, course, user))
        self.assertTrue(policy.delete(collaboration, course, user))

    def test_private_editors_are_owners(self):
        policy = PrivateEditorsAreOwners()
        collaboration = CollaborationFactory()
        course = None

        user = collaboration.user
        self.assertTrue(policy.read(collaboration, course, user))
        self.assertTrue(policy.edit(collaboration, course, user))
        self.assertTrue(policy.manage(collaboration, course, user))
        self.assertTrue(policy.delete(collaboration, course, user))

        user = UserFactory()  # random user
        self.assertFalse(policy.read(collaboration, course, user))
        self.assertFalse(policy.edit(collaboration, course, user))
        self.assertFalse(policy.manage(
            collaboration, course, user))
        self.assertFalse(policy.delete(
            collaboration, course, user))

        collaboration.group.user_set.add(user)  # now a group member
        self.assertTrue(policy.read(collaboration, course, user))
        self.assertTrue(policy.edit(collaboration, course, user))
        self.assertTrue(policy.manage(collaboration, course, user))
        self.assertTrue(policy.delete(collaboration, course, user))

        user = UserFactory(is_staff=True)
        self.assertTrue(policy.read(collaboration, course, user))
        self.assertFalse(policy.edit(collaboration, course, user))
        self.assertFalse(policy.manage(
            collaboration, course, user))
        self.assertFalse(policy.delete(
            collaboration, course, user))

    def test_private_student_faculty(self):
        policy = PrivateStudentAndFaculty()

        course = self.sample_course

        self.create_discussion(self.sample_course, self.instructor_one)
        discussions = get_course_discussions(self.sample_course)
        collaboration = Collaboration.objects.get_for_object(discussions[0])

        user = self.student_one
        self.assertFalse(policy.read(collaboration, course, user))
        self.assertFalse(policy.edit(collaboration, course, user))
        self.assertFalse(policy.manage(collaboration, course, user))
        self.assertFalse(policy.delete(collaboration, course, user))

        user = self.instructor_one
        self.assertTrue(policy.read(collaboration, course, user))
        self.assertTrue(policy.edit(collaboration, course, user))
        self.assertTrue(policy.manage(collaboration, course, user))
        self.assertTrue(policy.delete(collaboration, course, user))

        user = self.student_two
        self.assertFalse(policy.read(collaboration, course, user))
        self.assertFalse(policy.edit(collaboration, course, user))
        self.assertFalse(policy.manage(collaboration, course, user))
        self.assertFalse(policy.delete(collaboration, course, user))

    def test_instructor_shared(self):
        policy = InstructorShared()

        course = self.sample_course

        project = ProjectFactory.create(
            course=self.sample_course, author=self.student_one,
            policy='InstructorShared')
        collaboration = Collaboration.objects.get_for_object(project)

        user = self.student_one
        self.assertTrue(policy.read(collaboration, course, user))
        self.assertTrue(policy.edit(collaboration, course, user))
        self.assertTrue(policy.manage(collaboration, course, user))
        self.assertTrue(policy.delete(collaboration, course, user))

        user = self.student_two
        self.assertFalse(policy.read(collaboration, course, user))
        self.assertFalse(policy.edit(collaboration, course, user))
        self.assertFalse(policy.manage(collaboration, course, user))
        self.assertFalse(policy.delete(collaboration, course, user))

        user = self.instructor_one
        self.assertTrue(policy.read(collaboration, course, user))
        self.assertFalse(policy.edit(collaboration, course, user))
        self.assertFalse(policy.manage(collaboration, course, user))
        self.assertFalse(policy.delete(collaboration, course, user))

    def test_instructor_managed(self):
        policy = InstructorManaged()
        course = self.sample_course

        project = ProjectFactory.create(
            course=self.sample_course, author=self.student_one,
            policy='InstructorShared')
        collaboration = Collaboration.objects.get_for_object(project)

        user = self.student_one
        self.assertTrue(policy.read(collaboration, course, user))
        self.assertTrue(policy.edit(collaboration, course, user))
        self.assertTrue(policy.manage(collaboration, course, user))
        self.assertTrue(policy.delete(collaboration, course, user))

        user = self.student_two
        self.assertTrue(policy.read(collaboration, course, user))
        self.assertTrue(policy.edit(collaboration, course, user))
        self.assertFalse(policy.manage(collaboration, course, user))
        self.assertFalse(policy.delete(collaboration, course, user))

        user = self.instructor_one
        self.assertTrue(policy.read(collaboration, course, user))
        self.assertTrue(policy.edit(collaboration, course, user))
        self.assertTrue(policy.manage(collaboration, course, user))
        self.assertTrue(policy.delete(collaboration, course, user))

        course = self.alt_course

        user = self.alt_instructor
        self.assertFalse(policy.read(collaboration, course, user))
        self.assertFalse(policy.edit(collaboration, course, user))
        self.assertFalse(policy.manage(collaboration, course, user))
        self.assertFalse(policy.delete(collaboration, course, user))

        user = self.alt_student
        self.assertFalse(policy.read(collaboration, course, user))
        self.assertFalse(policy.edit(collaboration, course, user))
        self.assertFalse(policy.manage(collaboration, course, user))
        self.assertFalse(policy.delete(collaboration, course, user))

    def test_course_protected(self):
        policy = CourseProtected()

        course = self.sample_course

        project = ProjectFactory.create(
            course=self.sample_course, author=self.student_one,
            policy='CourseProtected')
        collaboration = Collaboration.objects.get_for_object(project)

        user = self.student_one
        self.assertTrue(policy.read(collaboration, course, user))
        self.assertTrue(policy.edit(collaboration, course, user))
        self.assertTrue(policy.manage(collaboration, course, user))
        self.assertTrue(policy.delete(collaboration, course, user))

        user = self.student_two
        self.assertTrue(policy.read(collaboration, course, user))
        self.assertFalse(policy.edit(collaboration, course, user))
        self.assertFalse(policy.manage(collaboration, course, user))
        self.assertFalse(policy.delete(collaboration, course, user))

        user = self.instructor_one
        self.assertTrue(policy.read(collaboration, course, user))
        self.assertFalse(policy.edit(collaboration, course, user))
        self.assertFalse(policy.manage(collaboration, course, user))
        self.assertFalse(policy.delete(collaboration, course, user))

    def test_assignment(self):
        policy = Assignment()

        course = self.sample_course

        assignment = ProjectFactory.create(
            course=self.sample_course, author=self.instructor_one,
            policy='Assignment')
        collaboration = Collaboration.objects.get_for_object(assignment)

        user = self.student_one
        self.assertTrue(policy.read(collaboration, course, user))
        self.assertFalse(policy.edit(collaboration, course, user))
        self.assertFalse(policy.manage(collaboration, course, user))
        self.assertFalse(policy.delete(collaboration, course, user))

        user = self.instructor_one
        self.assertTrue(policy.read(collaboration, course, user))
        self.assertTrue(policy.edit(collaboration, course, user))
        self.assertTrue(policy.manage(collaboration, course, user))
        self.assertTrue(policy.delete(collaboration, course, user))
