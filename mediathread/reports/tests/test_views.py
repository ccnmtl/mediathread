from django.core.urlresolvers import reverse
from django.test.client import RequestFactory
from django.test.testcases import TestCase

from mediathread.factories import MediathreadTestMixin, ProjectFactory


class ReportViewTest(MediathreadTestMixin, TestCase):

    def setUp(self):
        self.setup_sample_course()

        self.assignment1 = ProjectFactory.create(
            title='Alpha', course=self.sample_course,
            author=self.instructor_one, policy='Assignment')

        self.assignment2 = ProjectFactory.create(
            title='Beta', course=self.sample_course,
            author=self.instructor_one, policy='Assignment')

        ProjectFactory(title='Gamma', course=self.sample_course,
                       author=self.student_one, policy='CourseProtected')

        self.response1 = ProjectFactory.create(
            course=self.sample_course, author=self.student_one,
            policy='InstructorShared', parent=self.assignment1)
        self.response2 = ProjectFactory.create(
            course=self.sample_course, author=self.student_two,
            policy='InstructorShared', parent=self.assignment1)

    def test_class_assignment_report(self):
        url = reverse('class-assignment-report', args=[self.assignment1.id])

        # as student
        self.client.login(username=self.student_one.username, password='test')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 403)

        # as instructor
        self.client.login(username=self.instructor_one.username,
                          password='test')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.context_data['assignment'],
                          self.assignment1)
        self.assertEquals(len(response.context_data['responses']), 2)

    def test_class_assignments(self):
        url = reverse('class-assignments')

        # as student
        self.client.login(username=self.student_one.username, password='test')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 403)

        # as instructor
        self.client.login(username=self.instructor_one.username,
                          password='test')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.context_data['num_students'], 3)
        self.assertEquals(len(response.context_data['assignments']), 2)
        self.assertEquals(response.context_data['assignments'][0],
                          self.assignment1)
        self.assertEquals(response.context_data['assignments'][1],
                          self.assignment2)

    def test_class_summary(self):
        url = reverse('class-summary')

        # as student
        self.client.login(username=self.student_one.username, password='test')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 403)

        # as instructor
        self.client.login(username=self.instructor_one.username,
                          password='test')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(response.context_data['students']), 5)
