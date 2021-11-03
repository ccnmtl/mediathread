# pylint: disable-msg=R0904
from datetime import datetime, timedelta

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.http.response import Http404
from django.test import TestCase, RequestFactory
from django.urls import reverse
import json
from mediathread.factories import MediathreadTestMixin, UserFactory, \
    AssetFactory, SherdNoteFactory, ProjectFactory, AssignmentItemFactory, \
    ProjectNoteFactory
from mediathread.projects.models import (
    Project,
    RESPONSE_VIEW_POLICY, RESPONSE_VIEW_NEVER, RESPONSE_VIEW_SUBMITTED,
    PUBLISH_WHOLE_WORLD, PUBLISH_WHOLE_CLASS,
    PROJECT_TYPE_SELECTION_ASSIGNMENT,
    PROJECT_TYPE_SEQUENCE_ASSIGNMENT, ProjectNote, ProjectSequenceAsset,
    PUBLISH_DRAFT)
from mediathread.projects.tests.factories import ProjectSequenceAssetFactory
from mediathread.projects.views import (
    SelectionAssignmentView, ProjectItemView,
    SequenceAssignmentView, ProjectListView,
    AssignmentListView)
import reversion
from reversion.models import Version
from structuredcollaboration.models import Collaboration
import unittest


class ContextProcessorTest(MediathreadTestMixin, TestCase):

    def setUp(self):
        self.setup_sample_course()


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
            title=None, is_global_annotation=True)
        self.instructor_note = SherdNoteFactory(
            asset=self.asset1, author=self.instructor_one,
            tags=',image, instructor_one_selection,',
            body='instructor one selection note', range1=0, range2=1)
        self.instructor_ga = SherdNoteFactory(
            asset=self.asset1, author=self.instructor_one,
            tags=',image, instructor_one_item,',
            body='instructor one item note',
            title=None, is_global_annotation=True)

        # Sample Course Projects
        with reversion.create_revision():
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
        self.switch_course(self.client, self.sample_course)

        # Forbidden to save or view
        url = '/project/save/%s/' % self.project_private.id
        response = self.client.post(url, follow=True,
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEquals(response.status_code, 403)

    def test_project_save_nonajax(self):
        self.assertTrue(
            self.client.login(username=self.student_one.username,
                              password='test'))

        data = {u'body': [u'<p>no ajax here</p>'],
                u'participants': [self.student_one.id],
                u'publish': [u'PrivateEditorsAreOwners'],
                u'title': [u'Private Student Essay']}

        url = '/project/save/%s/' % self.project_private.id
        response = self.client.post(url, data)
        self.assertEquals(response.status_code, 302)

    def test_project_save_valid(self):
        versions = Version.objects.get_for_object(
            self.project_private).get_unique()
        self.assertEquals(sum(1 for v in versions), 1)

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
        self.assertFalse(the_json["is_essay_assignment"])
        self.assertEquals(the_json["title"], "Private Student Essay")
        self.assertEquals(the_json["revision"]["visibility"], "Draft")
        self.assertIsNone(the_json["revision"]["public_url"])
        self.assertEquals(the_json["revision"]["due_date"], "")

        project = Project.objects.get(id=self.project_private.id)
        self.assertEquals(project.author, self.student_one)
        self.assertIn(self.student_one, project.participants.all())
        self.assertIn(self.student_two, project.participants.all())

        versions = Version.objects.get_for_object(
            self.project_private).get_unique()
        self.assertEquals(sum(1 for v in versions), 2)

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
            '/course/{}/project/view/'.format(self.sample_course.id)))

        project = Project.objects.get(course=self.sample_course,
                                      title='Untitled')

        versions = Version.objects.get_for_object(project).get_unique()
        self.assertEquals(sum(1 for v in versions), 1)
        self.assertIsNone(project.date_submitted)
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

        versions = Version.objects.get_for_object(project).get_unique()
        self.assertEquals(sum(1 for v in versions), 2)
        self.assertIsNotNone(project.date_submitted)

    def test_assignment_response_create(self):
        self.client.login(username=self.student_one.username,
                          password='test')

        data = {u'participants': [self.student_one.id],
                u'publish': [u'PrivateEditorsAreOwners'],
                u'parent': self.assignment.pk}

        response = self.client.post('/project/create/', data)
        self.assertEquals(response.status_code, 302)

    def test_project_delete(self):
        ctype = ContentType.objects.get(model='project', app_label='projects')
        project_id = self.project_private.id
        url = reverse('project-delete', args=[project_id])

        # anonymous
        response = self.client.post(url, {})
        self.assertEquals(response.status_code, 302)

        # as non-owner
        self.client.login(username=self.student_two.username, password='test')
        self.switch_course(self.client, self.sample_course)
        response = self.client.post(url, {})
        self.assertEquals(response.status_code, 403)

        # as owner -- success
        self.client.login(username=self.student_one.username, password='test')
        self.switch_course(self.client, self.sample_course)
        response = self.client.post(url, {})
        self.assertEquals(response.status_code, 302)
        self.assertIsNone(Project.objects.filter(id=project_id).first())
        with self.assertRaises(Collaboration.DoesNotExist):
            Collaboration.objects.get(content_type=ctype,
                                      object_pk=project_id)

        # invalid project id
        url = reverse('project-delete', args=[213456])
        response = self.client.post(url, {})
        self.assertEquals(response.status_code, 404)

    def test_assignment_delete(self):
        ctype = ContentType.objects.get(model='project', app_label='projects')
        response1 = ProjectFactory.create(
            title='Zeta', course=self.sample_course, author=self.student_three,
            date_submitted=datetime.now(), policy='PublicEditorsAreOwners',
            parent=self.assignment)
        self.assertEquals(response1.assignment(), self.assignment)

        response2 = ProjectFactory.create(
            title='Omega', course=self.sample_course, author=self.student_one,
            policy='PrivateEditorsAreOwners', parent=self.assignment)
        self.assertEquals(response1.assignment(), self.assignment)

        project_id = self.assignment.id
        url = reverse('project-delete', args=[project_id])
        self.client.login(username=self.instructor_one.username,
                          password='test')
        self.switch_course(self.client, self.sample_course)
        response = self.client.post(url, {})
        self.assertEquals(response.status_code, 302)

        with self.assertRaises(Project.DoesNotExist):
            Project.objects.get(id=project_id)

        with self.assertRaises(Collaboration.DoesNotExist):
            Collaboration.objects.get(content_type=ctype,
                                      object_pk=project_id)

        self.assertIsNone(response1.assignment())
        self.assertIsNone(response2.assignment())

    def test_selection_assignment_delete(self):
        selection_assignment = ProjectFactory.create(
            course=self.sample_course, author=self.instructor_one,
            policy=PUBLISH_WHOLE_CLASS[0],
            project_type=PROJECT_TYPE_SELECTION_ASSIGNMENT)

        project_note = ProjectNoteFactory(project=selection_assignment,
                                          annotation=self.instructor_note)

        url = reverse('project-delete', args=[selection_assignment.id])
        self.client.login(username=self.instructor_one.username,
                          password='test')
        self.switch_course(self.client, self.sample_course)
        response = self.client.post(url, {})
        self.assertEquals(response.status_code, 302)

        with self.assertRaises(Project.DoesNotExist):
            Project.objects.get(id=selection_assignment.id)

        with self.assertRaises(ProjectNote.DoesNotExist):
            ProjectNote.objects.get(id=project_note.id)

    def test_sequence_assignment_response_delete(self):
        sequence_assignment = ProjectFactory.create(
            course=self.sample_course, author=self.instructor_one,
            policy=PUBLISH_WHOLE_CLASS[0],
            project_type=PROJECT_TYPE_SEQUENCE_ASSIGNMENT)
        response1 = ProjectFactory.create(
            title='Zeta', course=self.sample_course, author=self.student_one,
            parent=sequence_assignment)
        self.assertEquals(response1.assignment(), sequence_assignment)

        psa = ProjectSequenceAssetFactory(project=response1)

        url = reverse('project-delete', args=[response1.id])
        self.client.login(username=self.student_one.username,
                          password='test')
        response = self.client.post(url, {})
        self.assertEquals(response.status_code, 302)

        with self.assertRaises(Project.DoesNotExist):
            Project.objects.get(id=response1.id)

        with self.assertRaises(ProjectSequenceAsset.DoesNotExist):
            ProjectSequenceAsset.objects.get(id=psa.id)

    def test_unsubmit_response(self):
        assignment_response = ProjectFactory.create(
            course=self.sample_course, author=self.student_one,
            policy='PrivateEditorsAreOwners', parent=self.assignment)

        url = reverse('unsubmit-response')
        data = {'student-response': assignment_response.id}

        # anonymous
        response = self.client.post(url, data)
        self.assertEquals(response.status_code, 302)

        # as owner
        self.client.login(username=self.student_one.username, password='test')
        response = self.client.post(url, data)
        self.assertEquals(response.status_code, 403)

        # as faculty
        self.client.login(username=self.instructor_one.username,
                          password='test')
        self.switch_course(self.client, self.sample_course)
        response = self.client.post(url, data)
        self.assertEquals(response.status_code, 403)

        # resave the response as submitted
        assignment_response.create_or_update_collaboration('CourseProtected')
        assignment_response.date_submitted = datetime.now()
        assignment_response.save()

        self.client.login(username=self.instructor_one.username,
                          password='test')
        response = self.client.post(url, data, follow=True)
        self.assertEquals(response.status_code, 200)
        self.assertTrue(response.redirect_chain[0][0].startswith(
            '/project/view/'))

        assignment_response = Project.objects.get(id=assignment_response.id)
        self.assertFalse(assignment_response.is_submitted())
        collaboration = assignment_response.get_collaboration()
        self.assertEquals(collaboration.policy_record.policy_name,
                          'PrivateEditorsAreOwners')

    def test_update_visibility_view(self):
        assignment_response = ProjectFactory.create(
            course=self.sample_course, author=self.student_one,
            policy='CourseProtected', parent=self.assignment)

        url = reverse('project-visibility', args=[assignment_response.id])

        # anonymous
        response = self.client.post(url)
        self.assertEquals(response.status_code, 302)

        # as owner, no data
        self.client.login(username=self.student_one.username, password='test')
        response = self.client.post(url)
        self.assertEquals(response.status_code, 403)

        # with data
        data = {'publish': PUBLISH_WHOLE_WORLD[0]}
        response = self.client.post(url, data)
        self.assertEquals(response.status_code, 302)
        self.assertIsNotNone(assignment_response.public_url())

    def test_project_revisions(self):
        url = reverse('project-revisions',
                      args=[self.sample_course.id, self.project_private.id])

        response = self.client.get(url, {})
        self.assertEquals(response.status_code, 302)

        # forbidden as non-class participant
        self.client.login(username=self.alt_student.username, password='test')
        self.switch_course(self.client, self.alt_course)
        response = self.client.get(url, {})
        self.assertEquals(response.status_code, 403)

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
        self.assertEquals(len(response.context['versions']), 1)

    def test_project_view_readonly(self):
        version = next(self.project_private.versions())
        url = reverse('project-view-readonly',
                      kwargs={'project_id': self.project_private.id,
                              'version_number': version.revision_id})

        # anonymous
        response = self.client.get(url, {})
        self.assertEquals(response.status_code, 403)

        # forbidden
        self.client.login(username=self.student_two.username, password='test')
        response = self.client.get(url, {})
        self.assertEquals(response.status_code, 403)

        # owner
        self.client.login(username=self.student_one.username, password='test')
        response = self.client.get(url, {})
        self.assertEquals(response.status_code, 200)

        # ajax
        response = self.client.get(url, {},
                                   HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEquals(response.status_code, 200)

        the_json = json.loads(response.content)
        self.assertTrue('panels' in the_json)

    def test_project_public_view(self):
        url = self.project_private.get_collaboration().get_absolute_url()

        # still private
        response = self.client.get(url, {})
        self.assertEquals(response.status_code, 403)

        # reset to public
        self.project_private.create_or_update_collaboration(
            PUBLISH_WHOLE_WORLD[0])
        self.project_private.date_submitted = datetime.now()
        self.project_private.save()

        url = self.project_private.public_url()
        response = self.client.get(url, {})
        self.assertEquals(response.status_code, 200)

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

        self.assertEquals(len(the_json['panels']), 2)

        panel = the_json['panels'][0]
        self.assertFalse(panel['is_faculty'])
        self.assertEquals(len(panel['owners']), 6)
        self.assertEquals(panel['vocabulary'], [])
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
        self.switch_course(self.client, self.sample_course)

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
        self.switch_course(self.client, self.alt_course)
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

    def test_get_peer_response(self):
        view = SelectionAssignmentView()

        response = ProjectFactory.create(
            course=self.sample_course, author=self.student_two,
            policy='PrivateEditorsAreOwners', parent=self.assignment)

        url = reverse('project-workspace', args=[response.id])
        request = RequestFactory().get(url)
        request.course = self.sample_course
        request.user = self.student_one
        view.request = request

        self.assertEquals(response, view.get_peer_response(response))

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
        view.project = self.assignment

        ctx = view.get_context_data(project_id=self.assignment.id)
        self.assertEquals(ctx['assignment'], self.assignment)
        self.assertFalse(ctx['assignment_can_edit'])
        self.assertTrue(ctx['response_can_edit'])
        self.assertEquals(ctx['my_response'], response)
        self.assertEquals(ctx['the_response'], response)
        self.assertEquals(ctx['item'], self.asset)
        self.assertEquals(ctx['response_view_policies'], RESPONSE_VIEW_POLICY)
        self.assertEquals(ctx['submit_policy'], 'CourseProtected')
        self.assertTrue('vocabulary' in ctx)
        self.assertTrue('item_json' in ctx)

    def test_get_context_data_for_my_response(self):
        response = ProjectFactory.create(
            course=self.sample_course, author=self.student_one,
            policy='PrivateEditorsAreOwners', parent=self.assignment)

        url = reverse('project-workspace', args=[response.id])
        request = RequestFactory().get(url)
        request.course = self.sample_course
        request.user = self.student_one

        view = SelectionAssignmentView()
        view.request = request
        view.project = response

        ctx = view.get_context_data(project_id=response.id)
        self.assertEquals(ctx['assignment'], self.assignment)
        self.assertFalse(ctx['assignment_can_edit'])
        self.assertTrue(ctx['response_can_edit'])
        self.assertEquals(ctx['my_response'], response)
        self.assertEquals(ctx['the_response'], response)

    def test_get_context_data_for_a_response(self):
        response = ProjectFactory.create(
            course=self.sample_course, author=self.student_one,
            policy='PrivateEditorsAreOwners', parent=self.assignment)

        url = reverse('project-workspace', args=[response.id])
        request = RequestFactory().get(url)
        request.course = self.sample_course
        request.user = self.student_two

        view = SelectionAssignmentView()
        view.request = request
        view.project = response

        ctx = view.get_context_data(project_id=response.id)
        self.assertEquals(ctx['assignment'], self.assignment)
        self.assertFalse(ctx['assignment_can_edit'])
        self.assertFalse(ctx['response_can_edit'])
        self.assertIsNone(ctx['my_response'])
        self.assertEquals(ctx['the_response'], response)

    def test_public_view(self):
        assignment_response = ProjectFactory.create(
            date_submitted=datetime.now(),
            course=self.sample_course, author=self.student_one,
            policy=PUBLISH_WHOLE_WORLD[0], parent=self.assignment)

        response = self.client.get(assignment_response.public_url(), {})
        self.assertEquals(response.status_code, 403)


class SelectionAssignmentEditViewTest(MediathreadTestMixin, TestCase):

    def setUp(self):
        self.setup_sample_course()
        self.setup_alternate_course()

        self.project = ProjectFactory.create(
            course=self.sample_course, author=self.instructor_one,
            policy='PrivateEditorsAreOwners',
            project_type='selection-assignment')

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
        self.switch_course(self.client, self.sample_course)
        data = {
            'title': 'Updated',
            'body': 'Body Text',
            'item': asset1.id
        }
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


class SequenceAssignmentViewTest(MediathreadTestMixin, TestCase):

    def setUp(self):
        self.setup_sample_course()

        self.assignment = ProjectFactory.create(
            course=self.sample_course, author=self.instructor_one,
            policy='CourseProtected', project_type='sequence-assignment')

    def test_get_context_data_for_assignment(self):
        response = ProjectFactory.create(
            course=self.sample_course, author=self.student_one,
            policy='PrivateEditorsAreOwners', parent=self.assignment)

        url = reverse('project-workspace', args=[self.assignment.id])
        request = RequestFactory().get(url)
        request.course = self.sample_course
        request.user = self.student_one

        view = SequenceAssignmentView()
        view.request = request
        view.project = self.assignment

        ctx = view.get_context_data(project_id=self.assignment.id)
        self.assertEquals(ctx['assignment'], self.assignment)
        self.assertFalse(ctx['assignment_can_edit'])
        self.assertTrue(ctx['response_can_edit'])
        self.assertEquals(ctx['my_response'], response)
        self.assertEquals(ctx['the_response'], response)
        self.assertEquals(ctx['responses'], [response])
        self.assertTrue(ctx['show_instructions'])
        self.assertFalse(ctx['allow_public_compositions'])

    def test_get_context_data_my_response(self):
        response = ProjectFactory.create(
            course=self.sample_course, author=self.student_one,
            policy='PrivateEditorsAreOwners', parent=self.assignment)

        url = reverse('project-workspace', args=[response.id])
        request = RequestFactory().get(url)
        request.course = self.sample_course
        request.user = self.student_one

        view = SequenceAssignmentView()
        view.request = request
        view.project = self.assignment

        ctx = view.get_context_data(project_id=response.id)
        self.assertEquals(ctx['assignment'], self.assignment)
        self.assertFalse(ctx['assignment_can_edit'])
        self.assertTrue(ctx['response_can_edit'])
        self.assertEquals(ctx['my_response'], response)
        self.assertEquals(ctx['the_response'], response)
        self.assertEquals(ctx['responses'], [response])
        self.assertTrue(ctx['show_instructions'])

    def test_get_context_data_a_response(self):
        my_response = ProjectFactory.create(
            course=self.sample_course, author=self.student_one,
            policy='PrivateEditorsAreOwners', parent=self.assignment)

        response = ProjectFactory.create(
            course=self.sample_course, author=self.student_two,
            policy='PrivateEditorsAreOwners', parent=self.assignment)

        url = reverse('project-workspace', args=[response.id])
        request = RequestFactory().get(url)
        request.course = self.sample_course
        request.user = self.student_one

        view = SequenceAssignmentView()
        view.request = request
        view.project = self.assignment

        ctx = view.get_context_data(project_id=response.id)
        self.assertEquals(ctx['assignment'], self.assignment)
        self.assertFalse(ctx['assignment_can_edit'])
        self.assertFalse(ctx['response_can_edit'])
        self.assertEquals(ctx['my_response'], my_response)
        self.assertEquals(ctx['the_response'], response)
        self.assertEquals(ctx['responses'], [my_response])
        self.assertTrue(ctx['show_instructions'])

    def test_public_view(self):
        assignment_response = ProjectFactory.create(
            date_submitted=datetime.now(),
            course=self.sample_course, author=self.student_one,
            policy=PUBLISH_WHOLE_WORLD[0], parent=self.assignment)

        response = self.client.get(assignment_response.public_url(), {})
        self.assertEquals(response.status_code, 200)

        self.assertEquals(response.context['the_response'],
                          assignment_response)
        self.assertFalse(response.context['response_can_edit'])
        self.assertFalse(response.context['assignment_can_edit'])
        self.assertFalse(response.context['is_faculty'])
        self.assertIsNone(response.context['my_response'])
        self.assertIsNone(response.context['feedback'])
        self.assertEquals(response.context['responses'], [])


class CompositionAssignmentViewTest(MediathreadTestMixin, TestCase):

    def setUp(self):
        self.setup_sample_course()

        self.assignment = ProjectFactory.create(
            course=self.sample_course, author=self.instructor_one,
            policy='CourseProtected',
            project_type='assignment')

    def test_view(self):
        url = reverse('project-workspace',
                      args=[self.sample_course.id, self.assignment.id])

        # anonymous
        response = self.client.get(url, {})
        self.assertEquals(response.status_code, 302)

        # student
        self.client.login(username=self.student_one.username,
                          password='test')
        response = self.client.get(url, {})
        self.assertEquals(response.status_code, 200)

        # author
        self.client.login(username=self.instructor_one.username,
                          password='test')
        response = self.client.get(url, {})
        self.assertEquals(response.status_code, 200)

    def test_get_extra_context(self):
        url = reverse('project-workspace',
                      args=[self.sample_course.id, self.assignment.id])
        self.client.login(username=self.instructor_one.username,
                          password='test')
        response = self.client.get(url, {})
        self.assertEquals(response.status_code, 200)
        self.assertTrue(response.context_data['show_instructions'])

        self.client.login(username=self.student_one.username,
                          password='test')
        response = self.client.get(url, {})
        self.assertTrue(response.context_data['show_instructions'])

        response_one = ProjectFactory.create(
            course=self.sample_course, author=self.student_one,
            title='Student One Response',
            policy='PrivateEditorsAreOwners', parent=self.assignment)
        url = reverse('project-workspace',
                      args=[self.sample_course.id, response_one.id])

        response = self.client.get(url, {})
        self.assertTrue(response.context_data['show_instructions'])

        response_one.body = 'A brilliant response'
        response_one.save()
        response = self.client.get(url, {})
        self.assertFalse(response.context_data['show_instructions'])


class AssignmentEditViewTest(MediathreadTestMixin, TestCase):

    def setUp(self):
        self.setup_sample_course()
        self.setup_alternate_course()

        self.project = ProjectFactory.create(
            course=self.sample_course, author=self.instructor_one,
            policy='PrivateEditorsAreOwners',
            project_type='sequence-assignment')

    def test_get_edit(self):
        url = reverse('sequence-assignment-edit',
                      args=[self.sample_course.id, self.project.id])

        # anonymous
        response = self.client.get(url, {})
        self.assertEquals(response.status_code, 302)

        # alt course instructor
        self.client.login(username=self.alt_instructor.username,
                          password='test')
        self.switch_course(self.client, self.alt_course)
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
        url = reverse('sequence-assignment-create',
                      args=[self.sample_course.id])

        # faculty
        self.client.login(username=self.instructor_one.username,
                          password='test')
        response = self.client.get(url, {})
        self.assertEquals(response.status_code, 200)


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
            date_submitted=datetime.now())

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
        the_json = json.loads(response.content)
        self.assertEquals(len(the_json['assets']), 1)

        notes = list(the_json['assets'].values())[0]['annotations']
        for idx, note in enumerate(notes):
            self.assertEquals(note['id'], visible[idx][0])
            self.assertEquals(note['editable'], visible[idx][1])
            self.assertFalse(note['citable'])

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
        self.response_one.date_submitted = datetime.now()
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
        self.response_two.date_submitted = datetime.now()
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


class ProjectListViewTest(MediathreadTestMixin, TestCase):

    def setUp(self):
        self.setup_sample_course()
        self.setup_alternate_course()

    def test_get_project_owner_self(self):
        view = ProjectListView()
        url = reverse('project-list', args=[self.sample_course.id])
        view.request = RequestFactory().get(url)
        view.request.course = self.sample_course
        view.request.user = self.student_one
        self.assertEquals(view.get_project_owner(), self.student_one)

    def test_get_project_owner_invalid(self):
        view = ProjectListView()
        url = reverse('project-list', args=[self.sample_course.id])
        url = '{}?owner=foo'.format(url)
        view.request = RequestFactory().get(url)
        view.request.course = self.sample_course
        view.request.user = self.student_one

        with self.assertRaises((User.DoesNotExist, Http404)):
            view.get_project_owner()

    def test_get_project_owner_alt_course(self):
        view = ProjectListView()
        url = reverse('project-list', args=[self.sample_course.id])
        url = '{}?owner=alt_student'.format(url)
        view.request = RequestFactory().get(url)
        view.request.course = self.sample_course
        view.request.user = self.student_one

        with self.assertRaisesRegexp(Http404, 'not enrolled'):
            view.get_project_owner()

    def test_anonymous(self):
        url = reverse('project-list', args=[self.sample_course.id])
        response = self.client.get(url)
        self.assertEquals(response.status_code, 302)

    def test_get(self):
        # one assignment
        ProjectFactory.create(
            course=self.sample_course, author=self.instructor_one,
            policy='CourseProtected', project_type='assignment')

        url = reverse('project-list', args=[self.sample_course.id])
        self.client.login(username=self.student_one.username,
                          password='test')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)

        ctx = response.context_data
        self.assertEquals(ctx['object_list'].count(), 0)
        self.assertEquals(ctx['owner'].username, 'student_one')
        self.assertEquals(ctx['sortby'], 'title')
        self.assertEquals(ctx['direction'], 'asc')
        self.assertEquals(ctx['user_has_projects'], False)

    def test_get_sorted(self):
        self.client.login(username=self.student_one.username,
                          password='test')
        p1 = ProjectFactory.create(
                course=self.sample_course, author=self.student_one,
                title='A', policy='PrivateEditorsAreOwners')
        p2 = ProjectFactory.create(
                course=self.sample_course, author=self.student_one,
                title='B', policy='PrivateEditorsAreOwners')

        url = reverse('project-list', args=[self.sample_course.id])
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        ctx = response.context_data
        self.assertEquals(ctx['object_list'].count(), 2)
        self.assertEquals(ctx['object_list'][0], p1)
        self.assertEquals(ctx['object_list'][1], p2)
        self.assertEquals(ctx['sortby'], 'title')
        self.assertEquals(ctx['direction'], 'asc')
        self.assertEquals(ctx['user_has_projects'], True)

        url = '{}?direction=desc'.format(url)
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        ctx = response.context_data
        self.assertEquals(ctx['object_list'].count(), 2)
        self.assertEquals(ctx['object_list'][0], p2)
        self.assertEquals(ctx['object_list'][1], p1)
        self.assertEquals(ctx['direction'], 'desc')


class AssignmentListViewTest(MediathreadTestMixin, TestCase):

    def setUp(self):
        self.setup_sample_course()

    def test_anonymous(self):
        url = reverse('assignment-list', args=[self.sample_course.id])
        response = self.client.get(url)
        self.assertEquals(response.status_code, 302)

    def test_get(self):
        url = reverse('assignment-list', args=[self.sample_course.id])
        self.client.login(username=self.student_one.username,
                          password='test')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.context_data['status'], 'all')
        self.assertEquals(response.context_data['title'], '')

    def test_sort_by_full_name(self):
        self.client.login(username=self.instructor_one.username,
                          password='test')

        a1 = ProjectFactory.create(
            course=self.sample_course, author=self.instructor_one,
            policy='CourseProtected', project_type='assignment')
        a2 = ProjectFactory.create(
            course=self.sample_course, author=self.instructor_two,
            policy='CourseProtected', project_type='assignment')

        url = reverse('assignment-list', args=[self.sample_course.id])
        response = self.client.get(
            '{}?sortby=full_name&direction=asc'.format(url))
        self.assertEquals(response.status_code, 200)
        ctx = response.context_data
        self.assertEquals(ctx['object_list'].count(), 2)
        self.assertEquals(ctx['object_list'][0], a1)
        self.assertEquals(ctx['object_list'][1], a2)
        self.assertEquals(ctx['sortby'], 'full_name')
        self.assertEquals(ctx['direction'], 'asc')

        response = self.client.get(
            '{}?sortby=full_name&direction=desc'.format(url))
        self.assertEquals(response.status_code, 200)
        ctx = response.context_data
        self.assertEquals(ctx['object_list'].count(), 2)
        self.assertEquals(ctx['object_list'][0], a2)
        self.assertEquals(ctx['object_list'][1], a1)
        self.assertEquals(ctx['sortby'], 'full_name')
        self.assertEquals(ctx['direction'], 'desc')

    @unittest.skipIf(
        settings.DATABASES['default']['ENGINE'] !=
        'django.db.backends.postgresql_psycopg2',
        'This test exercises advanced querying functionality')
    def test_get_queryset(self):
        # Instructor assignments
        future_assignment = ProjectFactory.create(
            title='due tomorrow',
            course=self.sample_course, author=self.instructor_one,
            due_date=datetime.today() + timedelta(days=1),
            policy=PUBLISH_WHOLE_CLASS[0], project_type='assignment')
        evergreen_assignment = ProjectFactory.create(
            title='no due date',
            course=self.sample_course, author=self.instructor_one,
            policy=PUBLISH_WHOLE_CLASS[0], project_type='assignment')
        past_assignment = ProjectFactory.create(
            title='due yesterday',
            course=self.sample_course, author=self.instructor_one,
            due_date=datetime.today() - timedelta(days=1),
            policy=PUBLISH_WHOLE_CLASS[0], project_type='assignment')

        # Student responses

        # No response to the future assignment

        # Draft response for the evergreen assignment
        ProjectFactory.create(
            course=self.sample_course, author=self.student_one,
            date_submitted=None,
            policy=PUBLISH_DRAFT[0], parent=evergreen_assignment)

        # Submitted response for the past assignment
        submitted = datetime.today() - timedelta(days=2)
        ProjectFactory.create(
            course=self.sample_course, author=self.student_one,
            date_submitted=submitted,
            policy=PUBLISH_WHOLE_CLASS[0], parent=past_assignment)

        view = AssignmentListView()
        view.request = RequestFactory().get('/')
        view.request.course = self.sample_course
        view.request.user = self.student_one

        qs = view.get_queryset()
        self.assertEqual(qs.count(), 3)
        self.assertEqual(qs[0], future_assignment)
        self.assertTrue(qs[0].due_delta.days < 0)
        self.assertEqual(qs[1], evergreen_assignment)
        self.assertIsNone(qs[1].due_delta)
        self.assertEqual(qs[2], past_assignment)
        self.assertTrue(qs[2].due_delta.days > 0)
        self.assertEqual(qs[2].response_submitted, submitted)

        view.request = RequestFactory().get('/', {'status': 'draft'})
        view.request.course = self.sample_course
        view.request.user = self.student_one
        qs = view.get_queryset()
        self.assertEqual(qs.count(), 1)
        self.assertEqual(qs[0], evergreen_assignment)

        view.request = RequestFactory().get('/', {'status': 'submitted'})
        view.request.course = self.sample_course
        view.request.user = self.student_one
        qs = view.get_queryset()
        self.assertEqual(qs.count(), 1)
        self.assertEqual(qs[0], past_assignment)

        view.request = RequestFactory().get('/', {'status': 'no-response'})
        view.request.course = self.sample_course
        view.request.user = self.student_one
        qs = view.get_queryset()
        self.assertEqual(qs.count(), 1)
        self.assertEqual(qs[0], future_assignment)

        view.request = RequestFactory().get('/', {'title': 'tomorrow'})
        view.request.course = self.sample_course
        view.request.user = self.student_one
        qs = view.get_queryset()
        self.assertEqual(qs.count(), 1)
        self.assertEqual(qs[0], future_assignment)


class DiscussionAssignmentTest(MediathreadTestMixin, TestCase):

    def setUp(self):
        self.setup_sample_course()

        self.discussion = ProjectFactory.create(
            title='keep talking', course=self.sample_course,
            author=self.instructor_one, due_date=datetime.today(),
            policy=PUBLISH_WHOLE_CLASS[0],
            project_type='discussion-assignment')

    def test_create_wizard(self):
        url = reverse('discussion-assignment-create-wizard')

        # anonymous
        self.assertEqual(self.client.get(url).status_code, 302)

        # student
        self.client.login(username=self.student_one.username,
                          password='test')
        self.assertEqual(self.client.get(url).status_code, 403)

        # faculty
        self.client.login(username=self.instructor_one.username,
                          password='test')
        self.assertEqual(self.client.get(url).status_code, 200)

    def test_edit_wizard(self):
        url = reverse('discussion-assignment-edit-wizard',
                      args=[self.sample_course.id, self.discussion.id])

        # anonymous
        self.assertEqual(self.client.get(url).status_code, 302)

        # student
        self.client.login(username=self.student_one.username,
                          password='test')
        self.assertEqual(self.client.get(url).status_code, 403)

        # faculty
        self.client.login(username=self.instructor_one.username,
                          password='test')
        self.assertEqual(self.client.get(url).status_code, 200)

    def test_view(self):
        url = reverse('project-workspace',
                      args=[self.sample_course.id, self.discussion.id])

        # anonymous
        self.assertEqual(self.client.get(url).status_code, 302)

    def test_create(self):
        self.client.login(username=self.instructor_one.username,
                          password='test')
        data = {
            u'body': [u'<p>Talk</p>'],
            u'project_type': [u'discussion-assignment'],
            u'publish': [u'CourseProtected'],
            u'title': [u'Important Discussion']}
        url = reverse('discussion-assignment-create',
                      args=[self.sample_course.id])
        response = self.client.post(url, data, follow=True)
        self.assertEquals(response.status_code, 200)
        self.assertTrue(response.redirect_chain[0][0].startswith(
            '/course/{}/project/view/'.format(self.sample_course.id)))

        project = Project.objects.get(title='Important Discussion')
        discussion = project.course_discussion()
        self.assertEqual(discussion.comment, '<p>Talk</p>')
        self.assertEqual(discussion.title, 'Important Discussion')

        # faculty
        url = reverse('project-workspace',
                      args=[self.sample_course.id, project.id])
        self.assertEqual(self.client.get(url).status_code, 200)

        # student
        self.client.login(username=self.student_one.username,
                          password='test')
        self.assertEqual(self.client.get(url).status_code, 200)

    def test_save(self):
        pass
