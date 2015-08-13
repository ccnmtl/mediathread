# pylint: disable-msg=R0904
from json import loads
import json

from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import RequestFactory

from mediathread.factories import MediathreadTestMixin, UserFactory, \
    AssetFactory, SherdNoteFactory, ProjectFactory, AssignmentItemFactory, \
    ProjectNoteFactory
from mediathread.projects.models import Project, \
    RESPONSE_VIEW_POLICY, RESPONSE_VIEW_NEVER, RESPONSE_VIEW_SUBMITTED
from mediathread.projects.views import SelectionAssignmentView, ProjectItemView


class ProjectViewTest(MediathreadTestMixin, TestCase):
    def setUp(self):
        self.setup_sample_course()
        self.setup_alternate_course()

        # instructor that sees both Sample Course & Alternate Course
        self.instructor_three = UserFactory(username='instructor_three')
        self.add_as_faculty(self.sample_course, self.instructor_three)
        self.add_as_faculty(self.alt_course, self.instructor_three)

        # Sample Course Image Asset
        self.asset1 = AssetFactory.create(course=self.sample_course,
                                          primary_source='image')

        self.student_note = SherdNoteFactory(
            asset=self.asset1, author=self.student_one,
            tags=',student_one_selection',
            body='student one selection note', range1=0, range2=1)
        self.student_ga = SherdNoteFactory(
            asset=self.asset1, author=self.student_one,
            tags=',student_one_item',
            body='student one item note',
            title=None, range1=None, range2=None)
        self.instructor_note = SherdNoteFactory(
            asset=self.asset1, author=self.instructor_one,
            tags=',image, instructor_one_selection,',
            body='instructor one selection note', range1=0, range2=1)
        self.instructor_ga = SherdNoteFactory(
            asset=self.asset1, author=self.instructor_one,
            tags=',image, instructor_one_item,',
            body='instructor one item note',
            title=None, range1=None, range2=None)

        # Sample Course Projects
        self.project_private = ProjectFactory.create(
            course=self.sample_course, author=self.student_one,
            policy='PrivateEditorsAreOwners')
        self.add_citation(self.project_private, self.student_note)
        self.add_citation(self.project_private, self.student_ga)

        self.project_instructor_shared = ProjectFactory.create(
            course=self.sample_course, author=self.student_one,
            policy='InstructorShared')
        self.add_citation(self.project_instructor_shared, self.student_note)
        self.add_citation(self.project_instructor_shared, self.student_ga)

        self.project_class_shared = ProjectFactory.create(
            course=self.sample_course, author=self.student_one,
            policy='CourseProtected')
        self.add_citation(self.project_class_shared, self.student_note)
        self.add_citation(self.project_class_shared, self.student_ga)

        self.assignment = ProjectFactory.create(
            course=self.sample_course, author=self.instructor_one,
            policy='CourseProtected', project_type='assignment')

        # Alt Course Projects
        self.project_private_alt_course = ProjectFactory.create(
            course=self.alt_course, author=self.alt_student,
            policy='PrivateEditorsAreOwners')

        self.project_public_alt_course = ProjectFactory.create(
            course=self.alt_course, author=self.alt_student,
            policy='PrivateEditorsAreOwners')

    def test_project_save_doesnotexist(self):
        self.assertTrue(
            self.client.login(username=self.student_one.username,
                              password='test'))

        # Does not exist
        response = self.client.post('/project/save/1001/', {},
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEquals(response.status_code, 404)

    def test_project_save_cannot_edit(self):
        self.assertTrue(
            self.client.login(username=self.instructor_one.username,
                              password='test'))

        # Forbidden to save or view
        url = '/project/save/%s/' % self.project_private.id
        response = self.client.post(url, follow=True,
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEquals(response.status_code, 403)

    def test_project_save_nonajax(self):
        self.assertTrue(
            self.client.login(username=self.student_one.username,
                              password='test'))

        url = '/project/save/%s/' % self.project_private.id
        response = self.client.post(url)
        self.assertEquals(response.status_code, 405)

    def test_project_save_valid(self):
        self.assertTrue(self.client.login(username=self.student_one.username,
                                          password='test'))

        data = {u'body': [u'<p>abcdefghi</p>'],
                u'participants': [self.student_one.id, self.student_two.id],
                u'publish': [u'PrivateEditorsAreOwners'],
                u'title': [u'Private Student Essay']}

        url = '/project/save/%s/' % self.project_private.id
        response = self.client.post(url, data,
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEquals(response.status_code, 200)

        the_json = json.loads(response.content)
        self.assertEquals(the_json["status"], "success")
        self.assertFalse(the_json["is_assignment"])
        self.assertEquals(the_json["title"], "Private Student Essay")
        self.assertEquals(the_json["revision"]["visibility"], "Private")
        self.assertIsNone(the_json["revision"]["public_url"])
        self.assertEquals(the_json["revision"]["due_date"], "")

        project = Project.objects.get(id=self.project_private.id)
        self.assertEquals(project.author, self.student_one)
        self.assertIn(self.student_one, project.participants.all())
        self.assertIn(self.student_two, project.participants.all())

    def test_project_save_swap_authors(self):
        self.assertTrue(self.client.login(username=self.student_one.username,
                                          password='test'))

        data = {u'body': [u'<p>abcdefghi</p>'],
                u'participants': [self.student_one.id, self.student_two.id],
                u'publish': [u'PrivateEditorsAreOwners'],
                u'title': [u'Private Student Essay']}

        url = '/project/save/%s/' % self.project_private.id
        response = self.client.post(url, data,
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEquals(response.status_code, 200)

        self.assertTrue(self.client.login(username=self.student_two.username,
                                          password='test'))

        data = {u'body': [u'<p>the body here</p>'],
                u'participants': [self.student_two.id],
                u'publish': [u'PrivateEditorsAreOwners'],
                u'title': [u'Private Student Essay']}

        url = '/project/save/%s/' % self.project_private.id
        response = self.client.post(url, data,
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEquals(response.status_code, 200)

        project = Project.objects.get(id=self.project_private.id)
        self.assertEquals(project.author, self.student_two)
        self.assertNotIn(self.student_one, project.participants.all())
        self.assertIn(self.student_two, project.participants.all())

    def test_project_save_invalid_title(self):
        self.assertTrue(self.client.login(username=self.student_one.username,
                                          password='test'))

        data = {u'body': [u'<p>abcdefghi</p>'],
                u'participants': [self.student_one.id],
                u'publish': [u'PrivateEditorsAreOwners'],
                u'title': [u'']}

        url = '/project/save/%s/' % self.project_private.id
        response = self.client.post(url, data,
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEquals(response.status_code, 200)

        the_json = json.loads(response.content)
        self.assertEquals(the_json["status"], "error")
        self.assertTrue(the_json["msg"].startswith(' "" is not valid'))

    def test_project_create_and_save(self):
        self.assertTrue(self.client.login(username=self.student_one.username,
                                          password='test'))

        data = {u'title': [u'']}

        response = self.client.post('/project/create/', data, follow=True)
        self.assertEquals(response.status_code, 200)
        self.assertTrue(response.redirect_chain[0][0].startswith(
            'http://testserver/project/view/'))

        project = Project.objects.get(course=self.sample_course,
                                      title='Untitled')
        self.assertEquals(project.versions.count(), 1)
        self.assertIsNone(project.submitted_date())
        self.assertIn(self.student_one, project.participants.all())
        self.assertEquals(project.author, self.student_one)

        data = {u'body': [u'<p>abcdefghi</p>'],
                u'participants': [self.student_one.id],
                u'publish': [u'InstructorShared'],
                u'title': [u'Student Essay']}

        url = '/project/save/%s/' % project.id
        response = self.client.post(url, data,
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEquals(response.status_code, 200)

        project = Project.objects.get(title='Student Essay')
        self.assertEquals(project.versions.count(), 2)
        self.assertIsNotNone(project.submitted_date())

    def test_assignment_response_create(self):
        self.client.login(username=self.student_one.username,
                          password='test')

        data = {u'participants': [self.student_one.id],
                u'publish': [u'PrivateEditorsAreOwners'],
                u'parent': self.assignment.pk}

        response = self.client.post('/project/create/', data,
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEquals(response.status_code, 200)
        the_json = loads(response.content)
        project = the_json['context']['project']
        self.assertTrue(project['is_response'])

    def test_project_delete(self):
        project_id = self.project_private.id
        url = reverse('project-delete', args=[project_id])

        response = self.client.post(url, {})
        self.assertEquals(response.status_code, 302)

        # as non-owner
        self.client.login(username=self.student_two.username, password='test')
        self.switch_course(self.client, self.sample_course)
        response = self.client.post(url, {})
        self.assertEquals(response.status_code, 403)

        # as owner
        self.client.login(username=self.student_one.username, password='test')
        self.switch_course(self.client, self.sample_course)
        response = self.client.post(url, {})
        self.assertEquals(response.status_code, 302)
        self.assertIsNone(Project.objects.filter(id=project_id).first())

        # invalid project id
        url = reverse('project-delete', args=[213456])
        response = self.client.post(url, {})
        self.assertEquals(response.status_code, 404)

    def test_project_revisions(self):
        url = reverse('project-revisions', args=[self.project_private.id])

        response = self.client.get(url, {})
        self.assertEquals(response.status_code, 302)

        # forbidden as non-class participant
        self.client.login(username=self.alt_student.username, password='test')
        self.switch_course(self.client, self.alt_course)
        response = self.client.get(url, {})
        self.assertEquals(response.status_code, 404)

        # forbidden as non project-participant
        self.client.login(username=self.student_two.username, password='test')
        self.switch_course(self.client, self.sample_course)
        response = self.client.get(url, {})
        self.assertEquals(response.status_code, 403)

        # class participant
        self.client.login(username=self.student_one.username, password='test')
        self.switch_course(self.client, self.sample_course)
        response = self.client.get(url, {},
                                   HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEquals(response.status_code, 200)
        the_json = loads(response.content)
        self.assertTrue(len(the_json['revisions']) > 0)

    def test_project_workspace_errors(self):
        project_id = self.project_private.id
        url = reverse('project-workspace', args=[project_id])

        # invalid method
        response = self.client.post(url, {})
        self.assertEquals(response.status_code, 302)

        self.client.login(username=self.student_two.username, password='test')

        # as non-owner
        response = self.client.get(url)
        self.assertEquals(response.status_code, 403)

        # invalid project id
        url = reverse('project-workspace', args=[12345])
        response = self.client.get(url)
        self.assertEquals(response.status_code, 404)

    def test_project_workspace(self):
        project_id = self.project_private.id
        url = reverse('project-workspace', args=[project_id])

        # as owner
        self.client.login(username=self.student_one.username, password='test')
        response = self.client.get(url, {})
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.context['project'], self.project_private)
        self.assertEquals(response.context['space_owner'], 'student_one')
        self.assertFalse(response.context['show_feedback'])

    def test_project_workspace_ajax(self):
        project_id = self.project_private.id
        url = reverse('project-workspace', args=[project_id])

        # as owner
        self.client.login(username=self.student_one.username, password='test')
        response = self.client.get(url, {},
                                   HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEquals(response.status_code, 200)
        the_json = json.loads(response.content)

        self.assertEquals(the_json['space_owner'], 'student_one')
        self.assertFalse(the_json['show_feedback'])

        self.assertEquals(len(the_json['panels']), 2)

        panel = the_json['panels'][0]
        self.assertFalse(panel['is_faculty'])
        self.assertEquals(len(panel['owners']), 6)
        self.assertEquals(panel['vocabulary'], [])
        self.assertEquals(panel['panel_state'], 'open')
        self.assertEquals(panel['template'], 'project')
        self.assertEquals(len(panel['context']['annotations']), 2)
        self.assertEquals(len(panel['context']['assets']), 1)
        self.assertTrue(panel['context']['can_edit'])
        self.assertFalse(panel['context']['create_instructor_feedback'])
        self.assertFalse(panel['context']['editing'])
        self.assertTrue('form' in panel['context'])
        self.assertTrue('project' in panel['context'])
        self.assertEquals(panel['context']['response_count'], 0)
        self.assertEquals(panel['context']['responses'], [])
        self.assertEquals(panel['context']['type'], 'project')

    def test_project_workspace_collaborator(self):
        project_id = self.project_private.id
        url = reverse('project-workspace', args=[project_id])
        self.project_private.participants.add(self.student_two)
        self.project_private.create_or_update_collaboration(
            'PrivateEditorsAreOwners')

        self.client.login(username=self.student_two.username, password='test')
        response = self.client.get(url, {})
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.context['project'], self.project_private)
        self.assertEquals(response.context['space_owner'], 'student_two')
        self.assertFalse(response.context['show_feedback'])


class TestProjectSortView(MediathreadTestMixin, TestCase):

    def setUp(self):
        self.setup_sample_course()

    def test_basics(self):
        c = self.client
        url = reverse('project-sort')

        # anonymous
        response = c.post(url, {}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEquals(response.status_code, 302)

        # student
        c.login(username=self.student_one.username, password='test')
        response = c.post(url, {}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEquals(response.status_code, 403)

        # instructor, but no ajax
        c.login(username=self.instructor_one.username, password='test')
        response = c.post(url, {})
        self.assertEquals(response.status_code, 405)

    def test_sort(self):
        url = reverse('project-sort')
        c = self.client
        c.login(username=self.instructor_one.username, password='test')

        project1 = ProjectFactory.create(
            course=self.sample_course, author=self.instructor_one,
            policy='CourseProtected', ordinality=0)
        project2 = ProjectFactory.create(
            course=self.sample_course, author=self.instructor_one,
            policy='CourseProtected', ordinality=1)

        data = {'project': [project2.id, project1.id]}

        response = c.post(url, data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEquals(response.status_code, 200)

        # ordinality should be reversed
        project = Project.objects.get(id=project1.id)
        self.assertEquals(project.ordinality, 1)

        project = Project.objects.get(id=project2.id)
        self.assertEquals(project.ordinality, 0)


class SelectionAssignmentViewTest(MediathreadTestMixin, TestCase):

    def setUp(self):
        self.setup_sample_course()
        self.setup_alternate_course()

        self.assignment = ProjectFactory.create(
            course=self.sample_course, author=self.instructor_one,
            policy='PrivateEditorsAreOwners',
            project_type='selection-assignment')

        self.asset = AssetFactory.create(course=self.sample_course,
                                         primary_source='image')
        AssignmentItemFactory.create(project=self.assignment, asset=self.asset)

    def test_view(self):
        url = reverse('project-workspace', args=[self.assignment.id])

        # anonymous
        response = self.client.get(url, {})
        self.assertEquals(response.status_code, 302)

        # alt course instructor
        self.client.login(username=self.alt_instructor.username,
                          password='test')
        response = self.client.get(url, {})
        self.assertEquals(response.status_code, 403)

        # student
        self.client.login(username=self.student_one.username,
                          password='test')
        response = self.client.get(url, {})
        self.assertEquals(response.status_code, 403)

        # author
        self.client.login(username=self.instructor_one.username,
                          password='test')
        response = self.client.get(url, {})
        self.assertEquals(response.status_code, 200)

    def test_get_assignment(self):
        view = SelectionAssignmentView()
        self.assertEquals(self.assignment,
                          view.get_assignment(self.assignment))

        response = ProjectFactory.create(
            course=self.sample_course, author=self.student_one,
            policy='PrivateEditorsAreOwners', parent=self.assignment)
        self.assertEquals(self.assignment,
                          view.get_assignment(response))

    def test_get_my_response(self):
        view = SelectionAssignmentView()

        url = reverse('project-workspace', args=[self.assignment.id])
        request = RequestFactory().get(url)
        request.course = self.sample_course
        request.user = self.student_one
        view.request = request

        responses = self.assignment.responses(self.sample_course,
                                              self.student_one)
        self.assertIsNone(view.get_my_response(responses))

        response = ProjectFactory.create(
            course=self.sample_course, author=self.student_one,
            policy='PrivateEditorsAreOwners', parent=self.assignment)
        responses = self.assignment.responses(self.sample_course,
                                              self.student_one)
        self.assertEquals(response, view.get_my_response(responses))

    def test_get_context_data(self):
        response = ProjectFactory.create(
            course=self.sample_course, author=self.student_one,
            policy='PrivateEditorsAreOwners', parent=self.assignment)

        url = reverse('project-workspace', args=[self.assignment.id])
        request = RequestFactory().get(url)
        request.course = self.sample_course
        request.user = self.student_one

        view = SelectionAssignmentView()
        view.request = request

        ctx = view.get_context_data(project_id=self.assignment.id)
        self.assertEquals(ctx['assignment'], self.assignment)
        self.assertEquals(ctx['my_response'], response)
        self.assertEquals(ctx['item'], self.asset)
        self.assertEquals(ctx['response_view_policies'], RESPONSE_VIEW_POLICY)
        self.assertEquals(ctx['submit_policy'], 'CourseProtected')
        self.assertTrue('vocabulary' in ctx)
        self.assertTrue('item_json' in ctx)


class SelectionAssignmentEditViewTest(MediathreadTestMixin, TestCase):

    def setUp(self):
        self.setup_sample_course()
        self.setup_alternate_course()

        self.project = ProjectFactory.create(
            course=self.sample_course, author=self.instructor_one,
            policy='PrivateEditorsAreOwners',
            project_type='selection-assignment')

    def test_get_edit(self):
        url = reverse('selection-assignment-edit',
                      args=[self.project.id])

        # anonymous
        response = self.client.get(url, {})
        self.assertEquals(response.status_code, 302)

        # alt course instructor
        self.client.login(username=self.alt_instructor.username,
                          password='test')
        response = self.client.get(url, {})
        self.assertEquals(response.status_code, 403)

        # student
        self.client.login(username=self.student_one.username,
                          password='test')
        response = self.client.get(url, {})
        self.assertEquals(response.status_code, 403)

        # author
        self.client.login(username=self.instructor_one.username,
                          password='test')
        response = self.client.get(url, {})
        self.assertEquals(response.status_code, 200)

    def test_get_create(self):
        url = reverse('selection-assignment-create')

        # faculty
        self.client.login(username=self.instructor_one.username,
                          password='test')
        response = self.client.get(url, {})
        self.assertEquals(response.status_code, 200)

    def test_save(self):
        asset1 = AssetFactory.create(course=self.sample_course,
                                     primary_source='image')
        asset2 = AssetFactory.create(course=self.sample_course,
                                     primary_source='youtube')

        url = reverse('project-save', args=[self.project.id])

        # author
        self.client.login(username=self.instructor_one.username,
                          password='test')
        data = {
            'title': 'Updated',
            'body': 'Body Text',
            'item': asset1.id
        }
        response = self.client.post(url, data)
        self.assertEquals(response.status_code, 405)

        response = self.client.post(url, data,
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEquals(response.status_code, 200)

        # verify
        project = Project.objects.get(id=self.project.id)
        self.assertEquals(project.title, 'Updated')
        self.assertEquals(project.body, 'Body Text')
        self.assertEquals(project.assignmentitem_set.count(), 1)
        self.assertEquals(project.assignmentitem_set.first().asset, asset1)

        # swap out the asset
        data = {
            'title': 'Updated',
            'body': 'Body Text',
            'item': asset2.id
        }
        response = self.client.post(url, data,
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEquals(response.status_code, 200)
        self.assertEquals(project.assignmentitem_set.count(), 1)
        self.assertEquals(project.assignmentitem_set.first().asset, asset2)


class ProjectItemViewTest(MediathreadTestMixin, TestCase):

    def setUp(self):
        self.setup_sample_course()

        self.assignment = ProjectFactory.create(
            course=self.sample_course, author=self.instructor_one,
            policy='CourseProtected',
            project_type='selection-assignment')

        self.asset = AssetFactory.create(course=self.sample_course,
                                         primary_source='image')
        AssignmentItemFactory.create(project=self.assignment, asset=self.asset)

        self.response_one = ProjectFactory.create(
            course=self.sample_course, author=self.student_one,
            title="Student One Response",
            policy='PrivateEditorsAreOwners', parent=self.assignment)
        self.note_one = SherdNoteFactory(
            asset=self.asset, author=self.student_one,
            body='student one selection note', range1=0, range2=1)
        ProjectNoteFactory(project=self.response_one, annotation=self.note_one)

        self.response_two = ProjectFactory.create(
            course=self.sample_course, author=self.student_two,
            policy='PrivateEditorsAreOwners', parent=self.assignment)
        self.note_two = SherdNoteFactory(
            asset=self.asset, author=self.student_two,
            title="Student One Response",
            body='student two selection note', range1=0, range2=1)
        ProjectNoteFactory(project=self.response_two, annotation=self.note_two)

        ProjectFactory.create(
            course=self.sample_course, author=self.student_three,
            policy='CourseProtected', parent=self.assignment,
            submitted=True)

        url = reverse('project-item-view',
                      args=[self.assignment.id, self.asset.id])
        self.view = ProjectItemView()
        self.view.request = RequestFactory().get(url)
        self.view.request.course = self.sample_course

    def assert_visible_notes(self, viewer, visible,
                             editable=False, citable=False):
        self.view.request.user = viewer
        response = self.view.get(None, project_id=self.assignment.id,
                                 asset_id=self.asset.id)
        the_json = loads(response.content)
        self.assertEquals(len(the_json['assets']), 1)

        notes = the_json['assets'].values()[0]['annotations']
        for idx, note in enumerate(notes):
            self.assertEquals(note['id'], visible[idx][0])
            self.assertEquals(note['editable'], visible[idx][1])
            self.assertEquals(note['citable'], visible[idx][2])

    def test_get(self):
        # responses are not submitted
        # assignment is set to "always" response policy
        self.assert_visible_notes(self.student_one,
                                  [(self.note_one.id, True, False)])
        self.assert_visible_notes(self.student_two,
                                  [(self.note_two.id, True, False)])
        self.assert_visible_notes(self.instructor_one, [])

        # submit student one's response
        self.response_one.create_or_update_collaboration(
            'CourseProtected')
        self.response_one.submitted = True
        self.response_one.save()

        self.assert_visible_notes(self.student_one,
                                  [(self.note_one.id, False, True)])
        self.assert_visible_notes(self.student_two,
                                  [(self.note_one.id, False, True),
                                   (self.note_two.id, True, False)])
        self.assert_visible_notes(self.instructor_one,
                                  [(self.note_one.id, False, True)])

        # change assignment policy to never
        self.assignment.response_view_policy = RESPONSE_VIEW_NEVER[0]
        self.assignment.save()

        self.assert_visible_notes(self.student_one,
                                  [(self.note_one.id, False, False)])
        self.assert_visible_notes(self.student_two,
                                  [(self.note_two.id, True, False)])
        self.assert_visible_notes(self.instructor_one,
                                  [(self.note_one.id, False, False)])

        # change assignment policy to submitted
        self.assignment.response_view_policy = RESPONSE_VIEW_SUBMITTED[0]
        self.assignment.save()
        self.assert_visible_notes(self.student_one,
                                  [(self.note_one.id, False, False)])
        self.assert_visible_notes(self.student_two,
                                  [(self.note_two.id, True, False)])
        self.assert_visible_notes(self.instructor_one,
                                  [(self.note_one.id, False, False)])

        # submit student two's response
        # all students having submitted, the annotation is now citable
        self.response_two.create_or_update_collaboration(
            'CourseProtected')
        self.response_two.submitted = True
        self.response_two.save()

        self.assert_visible_notes(self.student_one,
                                  [(self.note_one.id, False, True),
                                   (self.note_two.id, False, True)])
        self.assert_visible_notes(self.student_two,
                                  [(self.note_one.id, False, True),
                                   (self.note_two.id, False, True)])
        self.assert_visible_notes(self.instructor_one,
                                  [(self.note_one.id, False, True),
                                   (self.note_two.id, False, True)])
