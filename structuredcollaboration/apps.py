from structuredcollaboration.models import CollaborationPolicyRecord
from structuredcollaboration.policies import CollaborationPolicy, \
    PublicEditorsAreOwners, PrivateEditorsAreOwners, InstructorManaged, \
    InstructorShared, PrivateStudentAndFaculty, CourseProtected, \
    CourseCollaboration

from django.apps import AppConfig


class CollaborationPolicyConfig(AppConfig):
    name = 'structuredcollaboration'

    def ready(self):
        CollaborationPolicyRecord.objects.register_policy(
            CollaborationPolicy, 'forbidden', 'Forbidden to everyone')

        CollaborationPolicyRecord.objects.register_policy(
            PublicEditorsAreOwners, 'PublicEditorsAreOwners',
            'Editors can manage the group, Content is world-readable')

        CollaborationPolicyRecord.objects.register_policy(
            PrivateEditorsAreOwners,
            'PrivateEditorsAreOwners',
            'User and group can view/edit/manage. Staff can read')

        CollaborationPolicyRecord.objects.register_policy(
            InstructorManaged,
            'InstructorManaged',
            'Instructors/Staff and user manage, Course members read')

        CollaborationPolicyRecord.objects.register_policy(
            InstructorShared,
            'InstructorShared',
            'group/user manage/edit and instructors can view')

        CollaborationPolicyRecord.objects.register_policy(
            PrivateStudentAndFaculty,
            'PrivateStudentAndFaculty',
            'Private between faculty and student')

        CollaborationPolicyRecord.objects.register_policy(
            CourseProtected,
            'CourseProtected',
            'Protected to Course Members')

        CollaborationPolicyRecord.objects.register_policy(
            CourseCollaboration, 'CourseCollaboration',
            'Course Collaboration')
