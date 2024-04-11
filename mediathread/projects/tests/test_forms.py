from django.test.client import RequestFactory
from django.test.testcases import TestCase

from mediathread.factories import MediathreadTestMixin, ProjectFactory
from mediathread.main.course_details import ALLOW_PUBLIC_COMPOSITIONS_KEY, \
    SELECTION_VISIBILITY_KEY
from mediathread.projects.forms import ProjectForm
from mediathread.projects.models import RESPONSE_VIEW_NEVER, \
    RESPONSE_VIEW_SUBMITTED, RESPONSE_VIEW_ALWAYS, PROJECT_TYPE_ASSIGNMENT, \
    PUBLISH_DRAFT, PUBLISH_WHOLE_CLASS, PROJECT_TYPE_SELECTION_ASSIGNMENT


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
        self.assertEqual(len(lst), 2)
        self.assertEqual(lst[0][0], PUBLISH_DRAFT[0])
        self.assertEqual(lst[1][0], PUBLISH_WHOLE_CLASS[0])

        # student
        self.request.user = self.student_one
        frm = ProjectForm(self.request, instance=None, data={})
        lst = frm.fields['publish'].choices
        self.assertEqual(len(lst), 3)
        self.assertEqual(lst[0][0], PUBLISH_DRAFT[0])
        self.assertEqual(lst[1][0], 'InstructorShared')
        self.assertEqual(lst[2][0], PUBLISH_WHOLE_CLASS[0])

        # maybe public option
        self.sample_course.add_detail(ALLOW_PUBLIC_COMPOSITIONS_KEY, 1)
        frm = ProjectForm(self.request, instance=None, data={})
        lst = frm.fields['publish'].choices
        self.assertEqual(len(lst), 3)
        self.assertEqual(lst[0][0], PUBLISH_DRAFT[0])
        self.assertEqual(lst[1][0], 'InstructorShared')
        self.assertEqual(lst[2][0], PUBLISH_WHOLE_CLASS[0])

    def test_project_form(self):
        frm = ProjectForm(self.request, instance=None, data={})

        lst = frm.fields['participants'].choices
        self.assertEqual(lst[0][1], 'Instructor One')
        self.assertEqual(lst[1][1], 'Instructor Two')
        self.assertEqual(lst[2][1], 'Student One')
        self.assertEqual(lst[3][1], 'Student Three')
        self.assertEqual(lst[4][1], 'Student Two')

        self.assertFalse(frm.fields['participants'].required)
        self.assertFalse(frm.fields['body'].required)
        self.assertFalse(frm.fields['submit'].required)
        self.assertFalse(frm.fields['publish'].required)
        self.assertFalse(frm.fields['response_view_policy'].required)

    def test_bound_composition_form(self):
        self.sample_course.add_detail(ALLOW_PUBLIC_COMPOSITIONS_KEY, 1)
        project = ProjectFactory.create(
            course=self.sample_course, author=self.student_one,
            policy=PUBLISH_DRAFT[0], response_view_policy='always')

        data = {}
        frm = ProjectForm(self.request, instance=project, data=data)
        self.assertEqual(frm.initial['publish'], PUBLISH_DRAFT[0])

        lst = frm.fields['publish'].choices
        self.assertEqual(len(lst), 3)
        self.assertEqual(lst[0][0], PUBLISH_DRAFT[0])
        self.assertEqual(lst[1][0], PUBLISH_WHOLE_CLASS[0])
        self.assertEqual(lst[2][0], 'PublicEditorsAreOwners')

    def test_bound_assignment_form(self):
        self.sample_course.add_detail(ALLOW_PUBLIC_COMPOSITIONS_KEY, 1)
        assignment = ProjectFactory.create(
            course=self.sample_course, author=self.student_one,
            policy=PUBLISH_DRAFT[0],
            project_type=PROJECT_TYPE_ASSIGNMENT)

        data = {}
        frm = ProjectForm(self.request, instance=assignment, data=data)
        self.assertEqual(frm.initial['publish'], PUBLISH_DRAFT[0])

        lst = frm.fields['publish'].choices
        self.assertEqual(len(lst), 2)
        self.assertEqual(lst[0][0], PUBLISH_DRAFT[0])
        self.assertEqual(lst[1][0], PUBLISH_WHOLE_CLASS[0])

    def test_bound_assignment_form_with_responses(self):
        self.sample_course.add_detail(ALLOW_PUBLIC_COMPOSITIONS_KEY, 1)
        assignment = ProjectFactory.create(
            course=self.sample_course, author=self.student_one,
            policy=PUBLISH_WHOLE_CLASS[0],
            project_type=PROJECT_TYPE_ASSIGNMENT)
        ProjectFactory.create(
            course=self.sample_course, author=self.student_one,
            title="Student One Response",
            policy=PUBLISH_WHOLE_CLASS[0], parent=assignment)

        data = {}
        frm = ProjectForm(self.request, instance=assignment, data=data)
        self.assertEqual(frm.initial['publish'], PUBLISH_WHOLE_CLASS[0])

        lst = frm.fields['publish'].choices
        self.assertEqual(len(lst), 1)
        self.assertEqual(lst[0][0], PUBLISH_WHOLE_CLASS[0])

    def test_response_policy_options(self):
        frm = ProjectForm(self.request, instance=None, data={})
        lst = frm.fields['response_view_policy'].choices
        self.assertEqual(len(lst), 3)
        self.assertEqual(lst[0], RESPONSE_VIEW_NEVER)
        self.assertEqual(lst[1], RESPONSE_VIEW_SUBMITTED)
        self.assertEqual(lst[2], RESPONSE_VIEW_ALWAYS)

        self.sample_course.add_detail(SELECTION_VISIBILITY_KEY, 0)
        frm = ProjectForm(self.request, instance=None, data={})
        lst = frm.fields['response_view_policy'].choices
        self.assertEqual(len(lst), 1)
        self.assertEqual(lst[0], RESPONSE_VIEW_NEVER)

    def test_bound_assignment_response_policy_options(self):
        self.sample_course.add_detail(SELECTION_VISIBILITY_KEY, 0)
        selection_assignment = ProjectFactory.create(
            course=self.sample_course, author=self.student_one,
            policy=PUBLISH_WHOLE_CLASS[0],
            project_type=PROJECT_TYPE_ASSIGNMENT)

        frm = ProjectForm(self.request, instance=selection_assignment, data={})
        lst = frm.fields['response_view_policy'].choices
        self.assertEqual(len(lst), 1)
        self.assertEqual(lst[0], RESPONSE_VIEW_NEVER)

        assignment = ProjectFactory.create(
            course=self.sample_course, author=self.instructor_one,
            policy=PUBLISH_WHOLE_CLASS[0],
            project_type=PROJECT_TYPE_SELECTION_ASSIGNMENT)

        frm = ProjectForm(self.request, instance=assignment, data={})
        lst = frm.fields['response_view_policy'].choices
        self.assertEqual(len(lst), 1)
        self.assertEqual(lst[0], RESPONSE_VIEW_NEVER)
