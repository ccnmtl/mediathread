from json import loads

from django.core.urlresolvers import reverse
from django.test.testcases import TestCase

from mediathread.djangosherd.models import SherdNote
from mediathread.factories import MediathreadTestMixin, ProjectFactory, \
    UserFactory, AssetFactory, SherdNoteFactory, RegistrationProfileFactory, \
    UserProfileFactory


class ReportViewTest(MediathreadTestMixin, TestCase):

    def setUp(self):
        self.setup_sample_course()

        self.asset1 = AssetFactory(course=self.sample_course)
        global_annotation, created = SherdNote.objects.global_annotation(
            self.asset1, self.student_three, auto_create=True)
        self.assertTrue(global_annotation.is_global_annotation())

        whole_item_annotation = SherdNoteFactory(
            asset=self.asset1, author=self.student_three,
            title="Whole Item Selection", range1=0, range2=0)
        self.assertFalse(whole_item_annotation.is_global_annotation())

        real_annotation = SherdNoteFactory(
            asset=self.asset1, author=self.student_three,
            title="Selection", range1=116.25, range2=6.75)
        self.assertFalse(real_annotation.is_global_annotation())

        self.assignment1 = ProjectFactory.create(
            title='Alpha', course=self.sample_course,
            author=self.instructor_one, policy='Assignment')

        self.response1 = ProjectFactory.create(
            title="Response 1",
            course=self.sample_course, author=self.student_one,
            policy='InstructorShared', parent=self.assignment1)
        self.response2 = ProjectFactory.create(
            title="Response 2", submitted=True,
            course=self.sample_course, author=self.student_two,
            policy='InstructorShared', parent=self.assignment1)

        self.assignment2 = ProjectFactory.create(
            title='Beta', course=self.sample_course,
            author=self.instructor_one, policy='Assignment')

        self.project = ProjectFactory(title='Gamma', course=self.sample_course,
                                      author=self.instructor_one,
                                      policy='CourseProtected')

        self.add_citation(self.project, global_annotation)
        self.add_citation(self.project, whole_item_annotation)
        self.add_citation(self.project, real_annotation)

    def test_class_assignments_report_logged_out(self):
        url = reverse('class-assignment-report', args=[self.assignment1.id])
        response = self.client.get(url)
        self.assertEquals(response.status_code, 403)

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

        # not an assignment
        url = reverse('class-assignment-report', args=[1232])
        response = self.client.get(url)
        self.assertEquals(response.status_code, 404)

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

    def test_class_activity_report(self):
        url = reverse('class-activity')
        self.create_discussion(self.sample_course, self.instructor_one)

        # as student
        self.client.login(username=self.student_one.username, password='test')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 403)

        # as instructor
        self.client.login(username=self.instructor_one.username,
                          password='test')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        self.assertTrue('my_feed' in response.context_data)
        self.assertIsNone(response.context_data['my_feed'].stuff)

        items = response.context_data['my_feed'].items.values()

        self.assertEquals(len(items), 3)
        self.assertEquals(items[0].content_object, self.asset1)
        self.assertEquals(items[1].content_object, self.response2)
        self.assertEquals(items[2].title, "Sample Course Discussion")

    def test_class_summary_graph(self):
        self.create_discussion(self.sample_course, self.instructor_one)

        url = reverse('class-summary-graph')

        # as student
        self.client.login(username=self.student_one.username, password='test')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 403)

        # as instructor
        self.client.login(username=self.instructor_one.username,
                          password='test')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        the_json = loads(response.content)

        self.assertEquals(len(the_json['links']), 0)
        self.assertEquals(len(the_json['nodes']), 6)
        self.assertEquals(the_json['nodes'][0]['nodeName'], 'Alpha')
        self.assertEquals(the_json['nodes'][1]['nodeName'], 'Response 1')
        self.assertEquals(the_json['nodes'][2]['nodeName'], 'Response 2')
        self.assertEquals(the_json['nodes'][3]['nodeName'], 'Beta')
        self.assertEquals(the_json['nodes'][4]['nodeName'], 'Gamma')
        self.assertEquals(the_json['nodes'][5]['nodeName'],
                          'Comment: Instructor One')

    def test_mediathread_activity_report(self):
        url = reverse('mediathread-activity-by-course')

        # as student
        self.client.login(username=self.student_one.username, password='test')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 302)

        # as instructor
        self.client.login(username=self.instructor_one.username,
                          password='test')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 302)

    def test_mediathread_activity_report_staff(self):
        url = reverse('mediathread-activity-by-course')

        # as superuser
        staff = UserFactory(is_staff=True, is_superuser=True)
        self.assertTrue(self.client.login(username=staff.username,
                                          password='test'))

        set_course_url = '/?set_course=%s&next=/' % \
            self.sample_course.group.name
        response = self.client.get(set_course_url, follow=True)
        self.assertEquals(response.status_code, 200)

        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)

    def test_self_registration_report(self):
        UserProfileFactory(user=self.student_one)
        RegistrationProfileFactory(user=self.student_one)
        url = reverse('mediathread-self-registration')

        # as student
        self.client.login(username=self.student_one.username, password='test')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 302)

        # as instructor
        self.client.login(username=self.instructor_one.username,
                          password='test')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 302)

        # as superuser
        staff = UserFactory(is_staff=True, is_superuser=True)
        self.assertTrue(self.client.login(username=staff.username,
                                          password='test'))

        set_course_url = '/?set_course=%s&next=/' % \
            self.sample_course.group.name
        response = self.client.get(set_course_url, follow=True)
        self.assertEquals(response.status_code, 200)

        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)

        header = ("First Name,Last Name,Email,Title,Institution,"
                  "Referred_By,User Story,Created")
        data = ("Student,One,,Title,Columbia University,Pablo Picasso,"
                "User Story,")

        self.assertTrue(header in response.content)
        self.assertTrue(data in response.content)
