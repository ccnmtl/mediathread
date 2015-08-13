from django.test.client import RequestFactory
from django.test.testcases import TestCase

from mediathread.factories import MediathreadTestMixin, ProjectFactory
from mediathread.main.course_details import ALLOW_PUBLIC_COMPOSITIONS_KEY, \
    SELECTION_VISIBILITY_KEY
from mediathread.projects.forms import ProjectForm
from mediathread.projects.models import RESPONSE_VIEW_NEVER, \
    RESPONSE_VIEW_SUBMITTED, RESPONSE_VIEW_ALWAYS, PROJECT_TYPE_ASSIGNMENT


class TestProjectForms(MediathreadTestMixin, TestCase):

    def setUp(self):
        self.setup_sample_course()
        self.request = RequestFactory().get('/')
        self.request.course = self.sample_course
        self.request.user = self.instructor_one

    def test_publish_options(self):
        # faculty
        self.request.user = self.instructor_one
        frm = ProjectForm(self.request, instance=None, data={})
        lst = frm.fields['publish'].choices
        self.assertEquals(len(lst), 2)
        self.assertEquals(lst[0][0], 'PrivateEditorsAreOwners')
        self.assertEquals(lst[1][0], 'CourseProtected')

        # student
        self.request.user = self.student_one
        frm = ProjectForm(self.request, instance=None, data={})
        lst = frm.fields['publish'].choices
        self.assertEquals(len(lst), 3)
        self.assertEquals(lst[0][0], 'PrivateEditorsAreOwners')
        self.assertEquals(lst[1][0], 'InstructorShared')
        self.assertEquals(lst[2][0], 'CourseProtected')

        # maybe public option
        self.sample_course.add_detail(ALLOW_PUBLIC_COMPOSITIONS_KEY, 1)
        frm = ProjectForm(self.request, instance=None, data={})
        lst = frm.fields['publish'].choices
        self.assertEquals(len(lst), 3)
        self.assertEquals(lst[0][0], 'PrivateEditorsAreOwners')
        self.assertEquals(lst[1][0], 'InstructorShared')
        self.assertEquals(lst[2][0], 'CourseProtected')

    def test_response_policy_options(self):
        frm = ProjectForm(self.request, instance=None, data={})
        lst = frm.fields['response_view_policy'].choices
        self.assertEquals(len(lst), 3)
        self.assertEquals(lst[0], RESPONSE_VIEW_NEVER)
        self.assertEquals(lst[1], RESPONSE_VIEW_SUBMITTED)
        self.assertEquals(lst[2], RESPONSE_VIEW_ALWAYS)

        self.sample_course.add_detail(SELECTION_VISIBILITY_KEY, 0)
        frm = ProjectForm(self.request, instance=None, data={})
        lst = frm.fields['response_view_policy'].choices
        self.assertEquals(len(lst), 1)
        self.assertEquals(lst[0], RESPONSE_VIEW_NEVER)

    def test_project_form(self):
        frm = ProjectForm(self.request, instance=None, data={})

        lst = frm.fields['participants'].choices
        self.assertEquals(lst[0][1], 'Instructor One')
        self.assertEquals(lst[1][1], 'Instructor Two')
        self.assertEquals(lst[2][1], 'Student One')
        self.assertEquals(lst[3][1], 'Student Three')
        self.assertEquals(lst[4][1], 'Student Two')

        self.assertFalse(frm.fields['participants'].required)
        self.assertFalse(frm.fields['body'].required)
        self.assertFalse(frm.fields['submit'].required)
        self.assertFalse(frm.fields['publish'].required)
        self.assertFalse(frm.fields['response_view_policy'].required)

    def test_bound_composition_form(self):
        self.sample_course.add_detail(ALLOW_PUBLIC_COMPOSITIONS_KEY, 1)
        project = ProjectFactory.create(
            course=self.sample_course, author=self.student_one,
            policy='PrivateEditorsAreOwners')

        data = {}
        frm = ProjectForm(self.request, instance=project, data=data)
        self.assertEquals(frm.initial['publish'], 'PrivateEditorsAreOwners')

        lst = frm.fields['publish'].choices
        self.assertEquals(len(lst), 3)
        self.assertEquals(lst[0][0], 'PrivateEditorsAreOwners')
        self.assertEquals(lst[1][0], 'CourseProtected')
        self.assertEquals(lst[2][0], 'PublicEditorsAreOwners')

    def test_bound_assignment_form(self):
        self.sample_course.add_detail(ALLOW_PUBLIC_COMPOSITIONS_KEY, 1)
        assignment = ProjectFactory.create(
            course=self.sample_course, author=self.student_one,
            policy='PrivateEditorsAreOwners',
            project_type=PROJECT_TYPE_ASSIGNMENT)

        data = {}
        frm = ProjectForm(self.request, instance=assignment, data=data)
        self.assertEquals(frm.initial['publish'], 'PrivateEditorsAreOwners')

        lst = frm.fields['publish'].choices
        self.assertEquals(len(lst), 2)
        self.assertEquals(lst[0][0], 'PrivateEditorsAreOwners')
        self.assertEquals(lst[1][0], 'CourseProtected')
