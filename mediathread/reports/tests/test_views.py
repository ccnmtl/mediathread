from datetime import datetime
from json import loads

from django.core.cache import cache
from django.urls import reverse
from django.test.client import RequestFactory
from django.test.testcases import TestCase

from mediathread.djangosherd.models import SherdNote
from mediathread.factories import MediathreadTestMixin, ProjectFactory, \
    UserFactory, AssetFactory, SherdNoteFactory, RegistrationProfileFactory, \
    UserProfileFactory
from mediathread.reports.views import AssignmentDetailReport
from mediathread.taxonomy.models import Term


class ReportViewTest(MediathreadTestMixin, TestCase):

    def setUp(self):
        self.setup_sample_course()

        self.asset1 = AssetFactory(course=self.sample_course)
        global_annotation, created = SherdNote.objects.global_annotation(
            self.asset1, self.student_three, auto_create=True)
        self.assertTrue(global_annotation.is_global_annotation)

        whole_item_annotation = SherdNoteFactory(
            asset=self.asset1, author=self.student_three,
            title="Whole Item Selection", range1=0, range2=0)
        self.assertFalse(whole_item_annotation.is_global_annotation)

        real_annotation = SherdNoteFactory(
            asset=self.asset1, author=self.student_three,
            title="Selection", range1=116.25, range2=6.75)
        self.assertFalse(real_annotation.is_global_annotation)

        self.assignment1 = ProjectFactory.create(
            title='Alpha', course=self.sample_course,
            author=self.instructor_one, policy='CourseProtected',
            project_type='assignment')

        self.response1 = ProjectFactory.create(
            title="Response 1",
            course=self.sample_course, author=self.student_one,
            policy='InstructorShared', parent=self.assignment1)
        self.response2 = ProjectFactory.create(
            title="Response 2", date_submitted=datetime.now(),
            course=self.sample_course, author=self.student_two,
            policy='InstructorShared', parent=self.assignment1)

        self.assignment2 = ProjectFactory.create(
            title='Beta', course=self.sample_course,
            author=self.instructor_one, policy='CourseProtected',
            project_type='assignment')

        self.project = ProjectFactory(title='Gamma', course=self.sample_course,
                                      author=self.instructor_one,
                                      policy='CourseProtected')

        self.add_citation(self.project, global_annotation)
        self.add_citation(self.project, whole_item_annotation)
        self.add_citation(self.project, real_annotation)

    def tearDown(self):
        cache.clear()

    def test_class_assignments_report_logged_out(self):
        url = reverse('class-assignment-report',
                      args=[self.sample_course.id, self.assignment1.id])
        response = self.client.get(url)
        self.assertEquals(response.status_code, 302)

    def test_class_assignment_report(self):
        url = reverse('class-assignment-report',
                      args=[self.sample_course.id, self.assignment1.id])

        # as student
        self.client.login(username=self.student_one.username, password='test')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 403)

        # as instructor
        self.client.login(username=self.instructor_one.username,
                          password='test')
        self.switch_course(self.client, self.sample_course)
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.context_data['assignment'],
                          self.assignment1)
        self.assertEquals(len(response.context_data['responses']), 2)

        # not an assignment
        url = reverse('class-assignment-report',
                      args=[self.sample_course.id, 1232])
        response = self.client.get(url)
        self.assertEquals(response.status_code, 404)

    def test_class_assignments(self):
        url = reverse('class-assignments', args=[self.sample_course.id])

        # as student
        self.client.login(username=self.student_one.username, password='test')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 403)

        # as instructor
        self.client.login(username=self.instructor_one.username,
                          password='test')
        self.switch_course(self.client, self.sample_course)
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.context_data['num_students'], 3)
        self.assertEquals(len(response.context_data['assignments']), 2)
        self.assertEquals(response.context_data['assignments'][0],
                          self.assignment1)
        self.assertEquals(response.context_data['assignments'][1],
                          self.assignment2)

    def test_class_summary(self):
        url = reverse('class-summary', args=[self.sample_course.id])

        # as student
        self.client.login(username=self.student_one.username, password='test')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 403)

        # as instructor
        self.client.login(username=self.instructor_one.username,
                          password='test')
        self.switch_course(self.client, self.sample_course)
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(response.context_data['students']), 5)

    def test_class_activity_report(self):
        url = reverse('class-activity', args=[self.sample_course.id])
        self.create_discussion(self.sample_course, self.instructor_one)

        # as student
        self.client.login(username=self.student_one.username, password='test')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 403)

        # as instructor
        self.client.login(username=self.instructor_one.username,
                          password='test')
        self.switch_course(self.client, self.sample_course)
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        self.assertTrue('my_feed' in response.context_data)
        self.assertIsNone(response.context_data['my_feed'].stuff)

        items = list(response.context_data['my_feed'].items.values())

        self.assertEquals(len(items), 3)
        self.assertEquals(items[0].content_object, self.asset1)
        self.assertEquals(items[1].content_object, self.response2)
        self.assertEquals(items[2].title, "Sample Course Discussion")

    def test_class_summary_graph(self):
        self.create_discussion(self.sample_course, self.instructor_one)

        url = reverse('class-summary-graph', args=[self.sample_course.id])

        # as student
        self.client.login(username=self.student_one.username, password='test')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 403)

        # as instructor
        self.client.login(username=self.instructor_one.username,
                          password='test')
        self.switch_course(self.client, self.sample_course)
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        the_json = loads(response.content)

        self.assertEquals(len(the_json['links']), 0)
        self.assertEquals(len(the_json['nodes']), 6)

        node_names = []
        for node in the_json['nodes']:
            node_names.append(node['nodeName'])

        self.assertTrue('Alpha' in node_names)
        self.assertTrue('Response 1' in node_names)
        self.assertTrue('Response 2' in node_names)
        self.assertTrue('Beta' in node_names)
        self.assertTrue('Gamma' in node_names)
        self.assertTrue('Comment: Instructor One' in node_names)

    def test_mediathread_activity_report(self):
        url = reverse('mediathread-activity-by-course',
                      args=[self.sample_course.id])

        # as student
        self.client.login(username=self.student_one.username, password='test')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 302)

        # as instructor
        self.client.login(username=self.instructor_one.username,
                          password='test')
        self.switch_course(self.client, self.sample_course)
        response = self.client.get(url)
        self.assertEquals(response.status_code, 302)

    def test_mediathread_activity_report_staff(self):
        url = reverse('mediathread-activity-by-course',
                      args=[self.sample_course.id])

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
        url = reverse('mediathread-self-registration',
                      args=[self.sample_course.id])

        # as student
        self.client.login(username=self.student_one.username, password='test')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 302)

        # as instructor
        self.client.login(username=self.instructor_one.username,
                          password='test')
        self.switch_course(self.client, self.sample_course)
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
        data = ("Student,One,student_one@example.com,Title,"
                "Columbia University,Pablo Picasso,User Story,")

        self.assertContains(response, header)
        self.assertContains(response, data)


class TestAssignmentDetailReport(MediathreadTestMixin, TestCase):

    def setUp(self):
        self.setup_sample_course()

        self.assignment1 = ProjectFactory.create(
            title='Alpha', course=self.sample_course,
            author=self.instructor_one, policy='CourseProtected',
            project_type='assignment')

        self.response1 = ProjectFactory.create(
            title="Response 1",
            course=self.sample_course, author=self.student_one,
            policy='InstructorShared', parent=self.assignment1)

        self.asset = AssetFactory(course=self.sample_course)
        SherdNote.objects.global_annotation(
            self.asset, self.student_one, auto_create=True)
        self.student_one_selection1 = SherdNoteFactory(
            asset=self.asset, author=self.student_one,
            tags=',student_one_selection',
            title="Selection", range1=116.25, range2=6.75)
        self.student_one_selection2 = SherdNoteFactory(
            asset=self.asset, author=self.student_one,
            title="Selection", range1=116.25, range2=6.75)
        self.student_two_selection = SherdNoteFactory(
            asset=self.asset, author=self.student_two,
            title="Selection", range1=16.25, range2=2.75)

        self.add_citation(self.response1, self.student_one_selection1)
        self.add_citation(self.response1, self.student_two_selection)

    def test_citation_analysis(self):
        view = AssignmentDetailReport()
        items, selections = view.citation_analysis(self.response1.citations())
        self.assertEquals(items[0], self.asset)
        self.assertTrue(self.student_one_selection1 in selections)
        self.assertTrue(self.student_two_selection in selections)

    def test_tag_usage(self):
        selections = SherdNote.objects.filter(author=self.student_one)
        view = AssignmentDetailReport()

        self.assertAlmostEquals(view.tag_usage(selections), 33.33, 2)

    def test_vocab_usage(self):
        taxonomy = {'Colors': ['Red', 'Blue', 'Green']}
        self.create_vocabularies(self.sample_course, taxonomy)

        term = Term.objects.get(name='red')
        self.create_term_relationship(self.student_one_selection1, term)

        selections = SherdNote.objects.filter(author=self.student_one)
        view = AssignmentDetailReport()
        view.request = RequestFactory().get('/')
        view.request.course = self.sample_course

        self.assertAlmostEquals(view.vocabulary_usage(selections), 33.33, 2)

    def test_percent_used(self):
        selections = SherdNote.objects.filter(author=self.student_one)
        view = AssignmentDetailReport()

        self.assertEquals(view.percent_used(selections, 0), 0.0)
        self.assertEquals(view.percent_used(selections, 3), 100.0)

    def test_report_rows(self):
        view = AssignmentDetailReport()
        view.request = RequestFactory().get('/')
        view.request.course = self.sample_course

        responses = self.assignment1.responses(self.sample_course,
                                               self.instructor_one)
        rows = view.get_report_rows(responses)

        next(rows)  # header
        row = next(rows)
        self.assertEquals(row[0], 'Student One')
        self.assertEquals(row[1], 'student_one')
        self.assertEquals(row[2], 'Response 1')
        self.assertEquals(row[3], 'Shared with Instructor')
        self.assertIsNone(row[4])
        # row[5] modified date
        self.assertFalse(row[6])
        self.assertEquals(row[7], 2)  # selections
        self.assertEquals(row[8], 1)  # items
        self.assertEquals(row[9], 1)  # author selections
        self.assertEquals(row[10], 1)  # author items
        self.assertAlmostEqual(row[11], 33.33, 2)  # % author selections used
        self.assertAlmostEqual(row[12], 100.00)  # tag usage
        self.assertEquals(row[13], 0.0)  # vocab usage
        self.assertEquals(row[14], 3)  # all author selections
        self.assertEquals(row[15], 1)  # author collection

        with self.assertRaises(StopIteration):
            next(rows)

    def test_view(self):
        url = reverse('assignment-detail-report',
                      args=[self.sample_course.id, self.assignment1.id])

        # as student
        self.client.login(username=self.student_one.username, password='test')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 403)

        # as instructor
        self.client.login(username=self.instructor_one.username,
                          password='test')
        self.switch_course(self.client, self.sample_course)
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
