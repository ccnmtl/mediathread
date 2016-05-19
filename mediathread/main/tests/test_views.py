# pylint: disable-msg=R0904
# pylint: disable-msg=E1103
from datetime import datetime
import json

from courseaffils.columbia import CourseStringMapper
from courseaffils.models import Affil, Course
from courseaffils.tests.factories import AffilFactory, CourseFactory
from django.conf import settings
from django.contrib.auth.models import User, AnonymousUser
from django.core import mail
from django.core.urlresolvers import reverse
from django.http.response import Http404
from django.test import TestCase, override_settings
from django.test.client import Client, RequestFactory
from threadedcomments.models import ThreadedComment
from waffle.testutils import override_flag
from freezegun import freeze_time

from mediathread.assetmgr.models import Asset
from mediathread.discussions.utils import get_course_discussions
from mediathread.djangosherd.models import SherdNote
from mediathread.factories import (
    UserFactory, UserProfileFactory, MediathreadTestMixin,
    AssetFactory, ProjectFactory, SherdNoteFactory,
    CourseInvitationFactory
)
from mediathread.main import course_details
from mediathread.main.course_details import allow_public_compositions, \
    course_information_title, all_items_are_visible, all_selections_are_visible
from mediathread.main.forms import (
    ContactUsForm, RequestCourseForm, CourseActivateForm, AcceptInvitationForm)
from mediathread.main.models import CourseInvitation
from mediathread.main.tests.mixins import LoggedInUserTestMixin
from mediathread.main.views import (
    AffilActivateView,
    MigrateCourseView, ContactUsView,
    RequestCourseView, CourseSettingsView, CourseManageSourcesView,
    CourseRosterView, CourseAddUserByUNIView, CourseAcceptInvitationView)
from mediathread.projects.models import Project


class SimpleViewTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_index(self):
        # it should redirect us somewhere.
        response = self.client.get("/")
        self.assertEquals(response.status_code, 302)
        # for now, we don't care where. really, we
        # are just making sure it's not a 500 error
        # at this point

    def test_smoke(self):
        # run the smoketests. we don't care if they pass
        # or fail, we just want to make sure that the
        # smoketests themselves don't have an error
        self.client.get("/smoketest/")


class MigrateCourseViewTest(MediathreadTestMixin, TestCase):

    def setUp(self):
        self.setup_sample_course()
        self.setup_alternate_course()

        self.superuser = User.objects.create(username='ccnmtl',
                                             password='test',
                                             is_superuser=True,
                                             is_staff=True)

        # instructor that sees both Sample Course & Alternate Course
        self.instructor_three = UserFactory(username='instructor_three',
                                            first_name='Instructor',
                                            last_name='Three')
        self.add_as_faculty(self.sample_course, self.instructor_three)
        self.add_as_faculty(self.alt_course, self.instructor_three)

        self.sample_course = Course.objects.get(title='Sample Course')
        self.alt_course = Course.objects.get(title="Alternate Course")

        self.asset1 = AssetFactory.create(course=self.sample_course,
                                          primary_source='image')

        self.student_note = SherdNoteFactory(
            asset=self.asset1, author=self.student_one,
            tags=',student_one_selection',
            body='student one selection note', range1=0, range2=1)
        self.instructor_note = SherdNoteFactory(
            asset=self.asset1, author=self.instructor_one,
            tags=',image, instructor_one_selection,',
            body='instructor one selection note', range1=0, range2=1)
        self.instructor_ga = SherdNoteFactory(
            asset=self.asset1, author=self.instructor_one,
            tags=',image, instructor_one_global,',
            body='instructor one global note',
            title=None, range1=None, range2=None)
        self.instructor_two_ga = SherdNoteFactory(
            asset=self.asset1, author=self.instructor_two,
            tags=',instructor_two_global,',
            body='instructor two global note',
            title=None, range1=None, range2=None)

    def test_as_student(self):
        self.assertTrue(
            self.client.login(username=self.student_one.username,
                              password='test'))
        response = self.client.get('/dashboard/migrate/')
        self.assertEquals(response.status_code, 403)

    def test_not_logged_in(self):
        response = self.client.get('/dashboard/migrate/')
        self.assertEquals(response.status_code, 302)

    def test_get_context_data(self):
        request = RequestFactory().get('/dashboard/migrate/')
        request.user = self.instructor_three
        request.course = self.sample_course

        view = MigrateCourseView()
        view.request = request

        ctx = view.get_context_data()

        self.assertEquals(len(ctx['current_course_faculty']), 3)
        self.assertEquals(ctx['current_course_faculty'][0].username,
                          'instructor_one')
        self.assertEquals(ctx['current_course_faculty'][1].username,
                          'instructor_three')
        self.assertEquals(ctx['current_course_faculty'][2].username,
                          'instructor_two')

        self.assertEquals(len(ctx['available_courses']), 2)
        self.assertEquals(ctx['available_courses'][0].title,
                          'Alternate Course')
        self.assertEquals(ctx['available_courses'][1].title,
                          'Sample Course')

        request.user = self.superuser
        ctx = view.get_context_data()
        self.assertEquals(len(ctx['available_courses']), 2)
        self.assertEquals(ctx['available_courses'][0].title,
                          'Alternate Course')
        self.assertEquals(ctx['available_courses'][1].title,
                          'Sample Course')

    def test_post_invalidcourse(self):
        data = {'fromCourse': 42}

        request = RequestFactory().post('/dashboard/migrate/', data)
        request.user = self.superuser
        request.course = self.sample_course

        view = MigrateCourseView()
        view.request = request

        self.assertRaises(Http404, view.post, request)

    def test_post_on_behalf_of_student(self):
        data = {
            'fromCourse': self.alt_course.id,
            'on_behalf_of': self.alt_student.id
        }

        request = RequestFactory().post('/dashboard/migrate/', data)
        request.user = self.superuser
        request.course = self.sample_course

        view = MigrateCourseView()
        view.request = request
        response = view.post(request)

        the_json = json.loads(response.content)
        self.assertFalse(the_json['success'])

    def test_post_on_behalf_of_faculty(self):
        data = {
            'fromCourse': self.alt_course.id,
            'on_behalf_of': self.alt_instructor.id
        }

        request = RequestFactory().post('/dashboard/migrate/', data)
        request.user = self.superuser
        request.course = self.sample_course

        view = MigrateCourseView()
        view.request = request
        response = view.post(request)

        the_json = json.loads(response.content)
        self.assertFalse(the_json['success'])

    def test_migrate_asset(self):
        data = {'fromCourse': self.sample_course.id,
                'asset_ids[]': [self.asset1.id],
                'project_ids[]': []}

        # Migrate assets from SampleCourse into Alternate Course
        # test_instructor_three is a member of both courses
        request = RequestFactory().post('/dashboard/migrate/', data)
        request.user = self.instructor_three
        request.course = self.alt_course

        view = MigrateCourseView()
        view.request = request
        response = view.post(request)

        the_json = json.loads(response.content)
        self.assertTrue(the_json['success'])
        self.assertEquals(the_json['asset_count'], 1)
        self.assertEquals(the_json['project_count'], 0)
        self.assertEquals(the_json['note_count'], 3)

        new_asset = Asset.objects.get(course=self.alt_course,
                                      title=self.asset1.title)
        self.assertEquals(new_asset.sherdnote_set.count(), 2)

        # verify there is a global annotation for instructor three
        ga = new_asset.global_annotation(self.instructor_three, False)
        self.assertIsNone(ga.title)
        self.assertEquals(ga.tags, '')
        self.assertIsNone(ga.body)

        # verify there is a selection annotation for instructor three
        note = new_asset.sherdnote_set.get(title=self.instructor_note.title)
        self.assertEquals(note.tags, '')
        self.assertIsNone(note.body)
        self.assertFalse(note.is_global_annotation())

    def test_migrate_with_tags(self):
        data = {
            'fromCourse': self.sample_course.id,
            'asset_ids[]': [self.asset1.id],
            'project_ids[]': [],
            'include_tags': 'true',
            'include_notes': 'false'
        }

        # Migrate assets from SampleCourse into Alternate Course
        # test_instructor_three is a member of both courses
        request = RequestFactory().post('/dashboard/migrate/', data)
        request.user = self.instructor_three
        request.course = self.alt_course

        view = MigrateCourseView()
        view.request = request
        view.post(request)

        new_asset = Asset.objects.get(course=self.alt_course,
                                      title=self.asset1.title)
        self.assertEquals(new_asset.sherdnote_set.count(), 2)

        note = new_asset.sherdnote_set.get(title=self.instructor_note.title)
        self.assertEquals(note.tags, self.instructor_note.tags)
        self.assertIsNone(note.body)

        note = new_asset.global_annotation(self.instructor_three, False)
        self.assertEquals(
            note.tags,
            u',image, instructor_one_global,,instructor_two_global,')
        self.assertIsNone(note.body)

    def test_migrate_with_notes(self):
        data = {
            'fromCourse': self.sample_course.id,
            'asset_ids[]': [self.asset1.id],
            'project_ids[]': [],
            'include_tags': 'false',
            'include_notes': 'true',
        }

        # Migrate assets from SampleCourse into Alternate Course
        # test_instructor_three is a member of both courses
        request = RequestFactory().post('/dashboard/migrate/', data)
        request.user = self.instructor_three
        request.course = self.alt_course

        view = MigrateCourseView()
        view.request = request
        view.post(request)

        new_asset = Asset.objects.get(course=self.alt_course,
                                      title=self.asset1.title)
        self.assertEquals(new_asset.sherdnote_set.count(), 2)

        note = new_asset.sherdnote_set.get(title=self.instructor_note.title)
        self.assertEquals(note.tags, '')
        self.assertEquals(note.body, self.instructor_note.body)

        note = new_asset.global_annotation(self.instructor_three, False)
        self.assertEquals(note.tags, '')
        self.assertEquals(
            note.body,
            u'instructor one global noteinstructor two global note')

    def test_migrate_tags_and_notes(self):
        data = {
            'fromCourse': self.sample_course.id,
            'asset_ids[]': [self.asset1.id],
            'project_ids[]': [],
            'include_tags': 'true',
            'include_notes': 'true'
        }

        # Migrate assets from SampleCourse into Alternate Course
        # test_instructor_three is a member of both courses
        request = RequestFactory().post('/dashboard/migrate/', data)
        request.user = self.instructor_three
        request.course = self.alt_course

        view = MigrateCourseView()
        view.request = request
        view.post(request)

        new_asset = Asset.objects.get(course=self.alt_course,
                                      title=self.asset1.title)
        self.assertEquals(new_asset.sherdnote_set.count(), 2)

        note = new_asset.sherdnote_set.get(title=self.instructor_note.title)
        self.assertEquals(note.tags, self.instructor_note.tags)
        self.assertEquals(note.body, self.instructor_note.body)

        note = new_asset.global_annotation(self.instructor_three, False)
        self.assertEquals(
            note.tags,
            u',image, instructor_one_global,,instructor_two_global,')
        self.assertEquals(
            note.body,
            u'instructor one global noteinstructor two global note')

    def test_migrate_project(self):
        self.project1 = ProjectFactory.create(course=self.sample_course,
                                              author=self.instructor_one,
                                              policy='PublicEditorsAreOwners')

        self.add_citation(self.project1, self.instructor_note)
        self.add_citation(self.project1, self.student_note)
        self.assertEquals(len(self.project1.citations()), 2)

        data = {
            'fromCourse': self.sample_course.id,
            'asset_ids[]': [],
            'project_ids[]': [self.project1.id]
        }

        # Migrate assets from SampleCourse into Alternate Course
        # test_instructor_three is a member of both courses
        request = RequestFactory().post('/dashboard/migrate/', data)
        request.user = self.instructor_three
        request.course = self.alt_course

        view = MigrateCourseView()
        view.request = request
        response = view.post(request)

        the_json = json.loads(response.content)
        self.assertTrue(the_json['success'])
        self.assertEquals(the_json['asset_count'], 1)
        self.assertEquals(the_json['project_count'], 1)
        self.assertEquals(the_json['note_count'], 2)

        new_asset = Asset.objects.get(course=self.alt_course,
                                      title=self.asset1.title)
        self.assertEquals(new_asset.sherdnote_set.count(), 3)

        new_note = new_asset.sherdnote_set.get(title=self.student_note.title)
        self.assertEquals(new_note.author, self.instructor_three)

        new_note = new_asset.sherdnote_set.get(
            title=self.instructor_note.title)
        self.assertEquals(new_note.author, self.instructor_three)

        new_note = new_asset.sherdnote_set.get(title=None)
        self.assertEquals(new_note.author, self.instructor_three)
        self.assertTrue(new_note.is_global_annotation())

        new_project = Project.objects.get(
            course=self.alt_course, title=self.project1.title)
        self.assertEquals(len(new_project.citations()), 2)

    def test_migrate_materials_view_student(self):
        self.assertTrue(self.client.login(username=self.student_one.username,
                                          password="test"))

        response = self.client.get('/dashboard/migrate/materials/%s/' %
                                   self.sample_course.id, {},
                                   HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEquals(response.status_code, 403)

    def test_migrate_materials_sample_course(self):
        self.project1 = ProjectFactory.create(course=self.sample_course,
                                              author=self.instructor_one,
                                              policy='PrivateEditorsAreOwners')
        self.project2 = ProjectFactory.create(course=self.sample_course,
                                              author=self.instructor_one,
                                              policy='CourseProtected',
                                              project_type='assignment')

        self.assertTrue(self.client.login(
            username=self.instructor_three.username,
            password="test"))

        set_course_url = '/?set_course=%s&next=/' % \
            self.sample_course.group.name
        response = self.client.get(set_course_url, follow=True)
        self.assertEquals(response.status_code, 200)

        url = '/dashboard/migrate/materials/%s/' % self.sample_course.id

        response = self.client.get(url, {},
                                   HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEquals(response.status_code, 200)

        the_json = json.loads(response.content)
        self.assertEquals(the_json['course']['title'], 'Sample Course')
        self.assertEquals(len(the_json['assets']), 1)

        self.assertEquals(the_json['assets'][0]['title'],
                          self.asset1.title)
        self.assertEquals(the_json['assets'][0]['annotation_count'], 1)

        self.assertEquals(len(the_json['projects']), 1)
        self.assertEquals(the_json['projects'][0]['title'],
                          self.project2.title)

    def test_migrate_materials_alternate_course(self):
        self.assertTrue(self.client.login(
            username=self.instructor_three.username,
            password="test"))
        set_course_url = '/?set_course=%s&next=/' % \
            self.alt_course.group.name
        response = self.client.get(set_course_url, follow=True)
        self.assertEquals(response.status_code, 200)

        url = '/dashboard/migrate/materials/%s/' % self.alt_course.id

        response = self.client.get(url, {},
                                   HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEquals(response.status_code, 200)

        the_json = json.loads(response.content)
        self.assertEquals(the_json['course']['title'], 'Alternate Course')
        self.assertEquals(len(the_json['assets']), 0)
        self.assertEquals(len(the_json['projects']), 0)


class ContactUsViewTest(TestCase):

    def test_get_initial_anonymous(self):
        view = ContactUsView()
        view.request = RequestFactory().get('/contact/')
        view.request.session = {}
        view.request.user = AnonymousUser()
        initial = view.get_initial()

        self.assertIsNotNone(initial['issue_date'])
        self.assertFalse('name' in initial)
        self.assertFalse('email' in initial)
        self.assertFalse('username' in initial)

    def test_get_initial_not_anonymous(self):
        view = ContactUsView()
        view.request = RequestFactory().get('/contact/')
        view.request.session = {}
        view.request.user = UserFactory(first_name='Foo',
                                        last_name='Bar',
                                        email='foo@bar.com')

        initial = view.get_initial()
        self.assertIsNotNone(initial['issue_date'])
        self.assertEquals(initial['name'], 'Foo Bar')
        self.assertEquals(initial['email'], 'foo@bar.com')
        self.assertEquals(initial['username'], view.request.user.username)

        # a subsequent call using an anonymous session returns a clean initial
        view.request.session = {}
        view.request.user = AnonymousUser()
        initial = view.get_initial()
        self.assertIsNotNone(initial['issue_date'])
        self.assertFalse('name' in initial)
        self.assertFalse('email' in initial)
        self.assertFalse('username' in initial)

    def test_form_valid(self):
        view = ContactUsView()
        form = ContactUsForm()
        form.cleaned_data = {
            'issuer_date': datetime.now(),
            'name': 'Linus Torvalds',
            'username': 'ltorvalds',
            'email': 'sender@ccnmtl.columbia.edu',
            'course': 'Introduction to Linux',
            'category': 'View Image',
            'description': 'This is a problem'
        }

        with self.settings(SUPPORT_DESTINATION=None,
                           TASK_ASSIGNMENT_DESTINATION=None):
            view.form_valid(form)
            self.assertEqual(len(mail.outbox), 1)

            self.assertEqual(mail.outbox[0].subject,
                             'Mediathread Contact Us Request')
            self.assertEquals(mail.outbox[0].from_email,
                              settings.SERVER_EMAIL)
            self.assertEquals(mail.outbox[0].to,
                              ['sender@ccnmtl.columbia.edu'])

    def test_form_valid_with_support_destination(self):
        view = ContactUsView()
        form = ContactUsForm()
        form.cleaned_data = {
            'issuer_date': datetime.now(),
            'name': 'Linus Torvalds',
            'username': 'ltorvalds',
            'email': 'sender@ccnmtl.columbia.edu',
            'course': 'Introduction to Linux',
            'category': 'View Image',
            'description': 'This is a problem'
        }

        with self.settings(SUPPORT_DESTINATION='support@ccnmtl.columbia.edu',
                           TASK_ASSIGNMENT_DESTINATION=None):
            view.form_valid(form)
            self.assertEqual(len(mail.outbox), 1)

            self.assertEqual(mail.outbox[0].subject,
                             'Mediathread Contact Us Request')
            self.assertEquals(mail.outbox[0].from_email,
                              'sender@ccnmtl.columbia.edu')
            self.assertEquals(mail.outbox[0].to,
                              [settings.SUPPORT_DESTINATION])


class RequestCourseViewTest(TestCase):

    def test_form_valid(self):
        view = RequestCourseView()
        form = RequestCourseForm()
        form.cleaned_data = {
            'name': 'Test Instructor',
            'email': 'test_instructor@ccnmtl.columbia.edu',
            'uni': 'ttt123',
            'course': 'Test Course',
            'course_id': 'Test Course Id',
            'term': 'Fall',
            'year': '2014',
            'instructor': 'Test Instructor',
            'section_leader': 'Test Teachers Assistant',
            'start': datetime.now(),
            'end': datetime.now(),
            'students': 24,
            'assignments_required': True,
            'description': 'Description',
            'title': 'The Course',
            'pid': '123',
            'mid': '456',
            'type': 'action item',
            'owner': 'sdreher',
            'assigned_to': 'sdreher'
        }

        with self.settings(TASK_ASSIGNMENT_DESTINATION=None):
            view.form_valid(form)


class CourseSettingsViewTest(MediathreadTestMixin, TestCase):

    def setUp(self):
        self.setup_sample_course()

    def test_not_logged_in(self):
        response = self.client.get('/dashboard/settings/')
        self.assertEquals(response.status_code, 302)

    def test_as_student(self):
        self.assertTrue(
            self.client.login(username=self.student_one.username,
                              password='test'))
        response = self.client.get('/dashboard/settings/')
        self.assertEquals(response.status_code, 403)

    def test_get_context_data(self):
        request = RequestFactory().get('/dashboard/settings/')
        request.user = self.instructor_one
        request.course = self.sample_course

        view = CourseSettingsView()
        view.request = request

        ctx = view.get_context_data()

        self.assertEquals(ctx['course'], self.sample_course)
        self.assertEquals(ctx[course_details.ALLOW_PUBLIC_COMPOSITIONS_KEY],
                          course_details.ALLOW_PUBLIC_COMPOSITIONS_DEFAULT)

        self.assertEquals(ctx[course_details.SELECTION_VISIBILITY_KEY],
                          course_details.SELECTION_VISIBILITY_DEFAULT)

        self.assertEquals(ctx[course_details.ITEM_VISIBILITY_KEY],
                          course_details.ITEM_VISIBILITY_DEFAULT)

        self.assertEquals(ctx[course_details.COURSE_INFORMATION_TITLE_KEY],
                          course_details.COURSE_INFORMATION_TITLE_DEFAULT)

    def test_post_allow_public_compositions(self):
        self.assertTrue(
            self.client.login(username=self.instructor_one.username,
                              password='test'))
        self.switch_course(self.client, self.sample_course)
        project = ProjectFactory.create(
            course=self.sample_course, author=self.instructor_one,
            policy='PublicEditorsAreOwners')

        self.client.post(
            '/dashboard/settings/',
            {course_details.ALLOW_PUBLIC_COMPOSITIONS_KEY: 0})

        col = project.get_collaboration()
        self.assertEquals(col.policy_record.policy_name, 'CourseProtected')

    def test_post(self):
        self.assertTrue(
            self.client.login(username=self.instructor_one.username,
                              password='test'))
        self.switch_course(self.client, self.sample_course)
        data = {
            course_details.COURSE_INFORMATION_TITLE_KEY: "Foo",
            course_details.SELECTION_VISIBILITY_KEY: 0,
            course_details.ITEM_VISIBILITY_KEY: 0,
            course_details.ALLOW_PUBLIC_COMPOSITIONS_KEY: 1
        }

        response = self.client.post('/dashboard/settings/', data)
        self.assertEquals(response.status_code, 302)
        self.assertEquals(course_information_title(self.sample_course), "Foo")
        self.assertTrue(allow_public_compositions(self.sample_course))
        self.assertFalse(all_items_are_visible(self.sample_course))
        self.assertFalse(all_selections_are_visible(self.sample_course))

    def test_post_disabled_selection_visibility(self):
        self.client.login(username=self.instructor_one.username,
                          password='test')
        self.switch_course(self.client, self.sample_course)
        data = {course_details.ITEM_VISIBILITY_KEY: 0}

        response = self.client.post('/dashboard/settings/', data)
        self.assertEquals(response.status_code, 302)

        # unchanged from defaults
        self.assertEquals(course_information_title(self.sample_course),
                          'From Your Instructor')
        self.assertFalse(allow_public_compositions(self.sample_course))

        # updated
        self.assertFalse(all_items_are_visible(self.sample_course))
        self.assertFalse(all_selections_are_visible(self.sample_course))


class CourseManageSourcesViewTest(MediathreadTestMixin, TestCase):

    def setUp(self):
        self.setup_sample_course()
        self.enable_upload(self.sample_course)
        self.superuser = UserFactory(is_staff=True, is_superuser=True)

    def test_not_logged_in(self):
        response = self.client.get('/dashboard/sources/')
        self.assertEquals(response.status_code, 302)

    def test_as_student(self):
        self.assertTrue(
            self.client.login(username=self.student_one.username,
                              password='test'))
        response = self.client.get('/dashboard/sources/')
        self.assertEquals(response.status_code, 403)

    def test_get_context(self):
        request = RequestFactory().get('/dashboard/sources/')
        request.user = self.instructor_one
        request.course = self.sample_course

        view = CourseManageSourcesView()
        view.request = request

        ctx = view.get_context_data()
        self.assertEquals(ctx['course'], self.sample_course)
        self.assertEquals(list(ctx['suggested_collections']), [])
        self.assertEquals(ctx['space_viewer'], self.instructor_one)
        self.assertFalse(ctx['is_staff'])
        self.assertIsNotNone(ctx['uploader'])

    def test_post(self):
        self.assertTrue(
            self.client.login(username=self.instructor_one.username,
                              password='test'))
        self.switch_course(self.client, self.sample_course)
        data = {
            course_details.UPLOAD_PERMISSION_KEY:
            course_details.UPLOAD_PERMISSION_ADMINISTRATOR
        }

        self.client.post('/dashboard/sources/', data)
        self.assertTrue(course_details.can_upload(self.superuser,
                                                  self.sample_course))
        self.assertFalse(course_details.can_upload(self.instructor_one,
                                                   self.sample_course))
        self.assertFalse(course_details.can_upload(self.student_one,
                                                   self.sample_course))


class IsLoggedInViewTest(MediathreadTestMixin, TestCase):

    def setUp(self):
        self.setup_sample_course()
        self.setup_alternate_course()

        # instructor that sees both Sample Course & Alternate Course
        self.instructor_three = UserFactory(username='instructor_three')
        self.add_as_faculty(self.sample_course, self.instructor_three)
        self.add_as_faculty(self.alt_course, self.instructor_three)

        self.url = reverse('is_logged_in.js')

    def test_not_logged_in(self):
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 200)

        self.assertContains(response, '"current": false')
        self.assertContains(response, '"logged_in": false')
        self.assertContains(response, '"course_selected": false')
        self.assertContains(response, '"ready": false')
        self.assertNotContains(response, 'youtube_apikey')
        self.assertNotContains(response, 'flickr_apikey')

    def test_logged_in_no_course(self):
        self.client.login(username=self.instructor_three.username,
                          password='test')

        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 200)

        self.assertContains(response, '"current": false')
        self.assertContains(response, '"logged_in": true')
        self.assertContains(response, '"course_selected": false')
        self.assertContains(response, '"ready": false')
        self.assertNotContains(response, 'youtube_apikey')
        self.assertNotContains(response, 'flickr_apikey')

    def test_logged_in_with_course(self):
        self.client.login(username=self.instructor_three.username,
                          password='test')
        self.switch_course(self.client, self.sample_course)

        with self.settings(YOUTUBE_BROWSER_APIKEY="123",
                           DJANGOSHERD_FLICKR_APIKEY="456",
                           BOOKMARKLET_VERSION="2"):
            response = self.client.get(self.url, {'version': 2})
            self.assertEquals(response.status_code, 200)

            self.assertContains(response, '"current": true')
            self.assertContains(response, '"logged_in": true')
            self.assertContains(response, '"course_selected": true')
            self.assertContains(response, '"ready": true')
            self.assertContains(response, '"youtube_apikey": "123"')
            self.assertContains(response, '"flickr_apikey": "456"')


class IsLoggedInDataViewTest(MediathreadTestMixin, TestCase):
    def setUp(self):
        self.up = UserProfileFactory()
        self.setup_sample_course()

    def test_get_as_anonymous(self):
        r = self.client.get(reverse('is_logged_in'))
        self.assertEqual(r.status_code, 200)

        data = json.loads(r.content)
        self.assertEqual(data['logged_in'], False)
        self.assertEqual(data['course_selected'], False)
        self.assertNotIn('youtube_apikey', data)
        self.assertNotIn('flickr_apikey', data)

    def test_get_when_logged_in(self):
        self.client.login(username=self.up.user.username, password='test')
        r = self.client.get(reverse('is_logged_in'))
        self.assertEqual(r.status_code, 200)

        data = json.loads(r.content)
        self.assertEqual(data['logged_in'], True)
        self.assertEqual(data['course_selected'], False)
        self.assertEqual(data['course_name'], '')

    def test_get_when_course_is_selected(self):
        # TODO: Select the sample course for the user and
        # make sure the api keys are present.
        self.client.login(username=self.up.user.username, password='test')
        r = self.client.get(reverse('is_logged_in'))
        self.assertEqual(r.status_code, 200)

        data = json.loads(r.content)
        self.assertEqual(data['logged_in'], True)
        self.assertEqual(data['course_selected'], False)
        self.assertEqual(data['course_name'], '')


class CourseDeleteMaterialsViewTest(MediathreadTestMixin, TestCase):

    def setUp(self):
        self.setup_sample_course()
        self.setup_alternate_course()

        # Sample Course Image Asset
        self.faculty_asset = AssetFactory.create(course=self.sample_course,
                                                 author=self.instructor_one,
                                                 primary_source='image')
        self.student_asset = AssetFactory.create(course=self.sample_course,
                                                 author=self.student_one,
                                                 primary_source='image')

        self.student_note1 = SherdNoteFactory(
            asset=self.faculty_asset, author=self.student_one,
            tags=',image1', body='student note on student asset')
        self.student_note2 = SherdNoteFactory(
            asset=self.student_asset, author=self.student_one,
            tags=',image2', body='student note on faculty asset')
        self.faculty_note1 = SherdNoteFactory(
            asset=self.faculty_asset, author=self.instructor_one,
            tags=',image3', body='faculty note on faculty asset')
        self.faculty_note2 = SherdNoteFactory(
            asset=self.student_asset, author=self.instructor_one,
            tags=',image4', body='faculty note on student asset')

        self.alt_asset = AssetFactory.create(course=self.alt_course,
                                             author=self.alt_student,
                                             primary_source='image')
        self.alt_note = SherdNoteFactory(
            asset=self.alt_asset, author=self.alt_student,
            tags=',image1', body='student note on student asset')

        self.faculty_composition = ProjectFactory.create(
            course=self.sample_course, author=self.instructor_one,
            policy='InstructorShared')
        self.student_composition = ProjectFactory.create(
            course=self.sample_course, author=self.student_one,
            policy='CourseProtected')
        self.assignment = ProjectFactory.create(
            course=self.sample_course, author=self.instructor_one,
            policy='CourseProtected', project_type='assignment')
        self.assignment_response = ProjectFactory.create(
            course=self.sample_course, author=self.student_one,
            policy='PrivateEditorsAreOwners', parent=self.assignment)

        self.alt_composition = ProjectFactory.create(
            course=self.alt_course, author=self.student_one,
            policy='CourseProtected')

        self.discussion = self.create_discussion(
            self.sample_course, self.instructor_one)
        self.comment = self.add_comment(self.discussion, self.student_one)

        self.alt_discussion = self.create_discussion(
            self.alt_course, self.alt_instructor)
        self.alt_comment = self.add_comment(self.alt_discussion,
                                            self.alt_student)

        self.superuser = UserFactory(is_superuser=True, is_staff=True)
        self.add_as_faculty(self.sample_course, self.superuser)

    def verify_alt_course_materials(self):
        # alt course assets, notes & projects are intact
        assets = Asset.objects.filter(course=self.alt_course)
        self.assertEquals(self.alt_asset, assets.first())
        notes = SherdNote.objects.filter(asset__course=self.alt_course)
        self.assertEquals(self.alt_note, notes.first())
        projects = Project.objects.filter(course=self.alt_course)
        self.assertEquals(self.alt_composition, projects.first())

        self.assertEquals(get_course_discussions(self.alt_course),
                          [self.alt_discussion])
        comments = ThreadedComment.objects.filter(parent=self.alt_discussion)
        self.assertEquals(self.alt_comment, comments.first())

    def test_access(self):
        url = reverse('course-delete-materials')
        data = {'clear_all': True, 'username': self.student_one.username}

        self.client.login(username=self.student_one.username, password='test')
        response = self.client.post(url, data)
        self.assertEquals(response.status_code, 302)

    def test_clear_all(self):
        url = reverse('course-delete-materials')
        data = {'clear_all': True, 'username': self.superuser.username}

        self.client.login(username=self.superuser.username, password='test')
        self.switch_course(self.client, self.sample_course)

        response = self.client.post(url, data)
        self.assertEquals(response.status_code, 302)
        self.assertTrue('All requested materials were deleted'
                        in response.cookies['messages'].value)

        assets = Asset.objects.filter(course=self.sample_course)
        self.assertEquals(assets.count(), 0)
        notes = SherdNote.objects.filter(asset__course=self.sample_course)
        self.assertEquals(notes.count(), 0)
        projects = Project.objects.filter(course=self.sample_course)
        self.assertEquals(projects.count(), 0)

        self.assertEquals(get_course_discussions(self.sample_course),
                          [self.discussion])
        comments = ThreadedComment.objects.filter(parent=self.discussion)
        self.assertEquals(comments.count(), 0)

        self.verify_alt_course_materials()

    def test_clear_student_only(self):
        url = reverse('course-delete-materials')
        data = {'clear_all': False, 'username': self.superuser.username}

        self.client.login(username=self.superuser.username, password='test')
        self.switch_course(self.client, self.sample_course)

        response = self.client.post(url, data)
        self.assertEquals(response.status_code, 302)
        self.assertTrue('All requested materials were deleted'
                        in response.cookies['messages'].value)

        assets = Asset.objects.filter(course=self.sample_course)
        self.assertEquals(assets.count(), 1)
        self.assertEquals(assets.first(), self.faculty_asset)

        notes = SherdNote.objects.filter(asset__course=self.sample_course)
        self.assertEquals(notes.count(), 1)
        self.assertEquals(notes.first(), self.faculty_note1)

        projects = Project.objects.filter(course=self.sample_course)
        self.assertEquals(projects.count(), 2)
        self.assertTrue(self.faculty_composition in projects.all())
        self.assertTrue(self.assignment in projects.all())

        self.assertEquals(get_course_discussions(self.sample_course),
                          [self.discussion])
        comments = ThreadedComment.objects.filter(parent=self.discussion)
        self.assertEquals(comments.count(), 0)

        self.verify_alt_course_materials()


class CourseRosterViewsTest(MediathreadTestMixin, TestCase):

    def setUp(self):
        self.setup_sample_course()
        self.url = reverse('course-roster')

    def test_get(self):
        self.client.login(username=self.instructor_one.username,
                          password='test')
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 200)

    def test_roster_view_get_queryset(self):
        request = RequestFactory().get(self.url)
        request.user = self.instructor_one
        request.course = self.sample_course

        view = CourseRosterView()
        view.request = request

        qs = view.get_queryset()
        self.assertEquals(qs.count(), self.sample_course.members.count())

    def test_promote_demote_users(self):
        self.client.login(username=self.instructor_one.username,
                          password='test')
        self.switch_course(self.client, self.sample_course)

        url = reverse('course-roster-promote')
        data = {'student_id': self.student_one.id}
        response = self.client.post(url, data)

        self.assertEquals(response.status_code, 302)
        self.assertTrue(self.sample_course.is_faculty(self.student_one))

        url = reverse('course-roster-demote')
        data = {'faculty_id': self.student_one.id}
        response = self.client.post(url, data)
        self.assertEquals(response.status_code, 302)
        self.assertFalse(self.sample_course.is_faculty(self.student_one))

    def test_remove_user(self):
        self.client.login(username=self.instructor_one.username,
                          password='test')
        self.switch_course(self.client, self.sample_course)

        url = reverse('course-roster-remove')
        data = {'user_id': self.student_one.id}
        response = self.client.post(url, data)
        self.assertEquals(response.status_code, 302)
        self.assertFalse(self.sample_course.is_member(self.student_one))

        data = {'user_id': self.instructor_two.id}
        response = self.client.post(url, data)
        self.assertEquals(response.status_code, 302)
        self.assertFalse(self.sample_course.is_faculty(self.instructor_two))
        self.assertFalse(self.sample_course.is_member(self.instructor_two))

    def test_uni_invite_get_or_create_user(self):
        request = RequestFactory().get(self.url)
        request.user = self.instructor_one
        request.course = self.sample_course

        view = CourseAddUserByUNIView()
        view.request = request

        user = view.get_or_create_user('abc123')
        self.assertFalse(user.has_usable_password())
        self.assertEquals(user, view.get_or_create_user('abc123'))

    def test_uni_invite_post(self):
        self.client.login(username=self.instructor_one.username,
                          password='test')
        self.switch_course(self.client, self.sample_course)

        url = reverse('course-roster-add-uni')
        response = self.client.post(url, {})
        self.assertEquals(response.status_code, 302)
        self.assertTrue('Please enter a comma-separated list of UNIs'
                        in response.cookies['messages'].value)
        response.delete_cookie('messages')

        response = self.client.post(url, {'unis': 'abc123'})
        self.assertEquals(response.status_code, 302)
        user = User.objects.get(username='abc123')
        self.assertTrue(self.sample_course.is_true_member(user))

        user.first_name = 'John'
        user.last_name = 'Smith'
        user.email = 'jsmith@example.com'
        user.save()

        response = self.client.post(url, {'unis': ' abc123 ,efg456,'})
        self.assertEquals(response.status_code, 302)

        user = User.objects.get(username='efg456')
        self.assertTrue(self.sample_course.is_true_member(user))
        self.assertTrue('John Smith (abc123) is already a course member'
                        in response.cookies['messages'].value)
        self.assertTrue('efg456 is now a course member'
                        in response.cookies['messages'].value)

    def test_email_invite_existing_course_member(self):
        url = reverse('course-roster-invite-email')
        self.client.login(username=self.instructor_one.username,
                          password='test')
        self.switch_course(self.client, self.sample_course)
        response = self.client.post(url, {'emails': self.student_one.email})
        self.assertEquals(response.status_code, 302)
        self.assertTrue(
            'Student One (student_one@example.com) is already a course member'
            in response.cookies['messages'].value)

    def test_email_invite_existing_user(self):
        with self.settings(SERVER_EMAIL='mediathread@example.com'):
            self.setup_alternate_course()

            url = reverse('course-roster-invite-email')
            self.client.login(username=self.instructor_one.username,
                              password='test')
            self.switch_course(self.client, self.sample_course)
            response = self.client.post(url,
                                        {'emails': self.alt_student.email})
            self.assertEquals(response.status_code, 302)
            self.assertTrue('Student Alternate is now a course member'
                            in response.cookies['messages'].value)
            self.assertTrue(
                self.sample_course.is_true_member(self.alt_student))

            self.assertEqual(len(mail.outbox), 1)
            self.assertEqual(mail.outbox[0].subject,
                             'Mediathread: Sample Course')
            self.assertEquals(mail.outbox[0].from_email,
                              'mediathread@example.com')
            self.assertTrue(mail.outbox[0].to, [self.alt_student.email])
            self.assertTrue(CourseInvitation.objects.count() == 0)

    def test_email_invite_new_user(self):
        with self.settings(SERVER_EMAIL='mediathread@example.com'):
            url = reverse('course-roster-invite-email')
            self.client.login(username=self.instructor_one.username,
                              password='test')
            self.switch_course(self.client, self.sample_course)
            response = self.client.post(url, {'emails': 'foo@example.com'})

            self.assertEquals(response.status_code, 302)
            self.assertTrue('foo@example.com was invited to join the course'
                            in response.cookies['messages'].value)

            self.assertEqual(len(mail.outbox), 1)
            self.assertEqual(mail.outbox[0].subject,
                             'Mediathread Course Invitation: Sample Course')
            self.assertEquals(mail.outbox[0].from_email,
                              'mediathread@example.com')
            self.assertTrue(mail.outbox[0].to, ['foo@example.com'])
            self.assertTrue(CourseInvitation.objects.count() == 1)

            # reinvite the user. a new email will be sent w/existing invitation
            url = reverse('course-roster-invite-email')
            self.client.login(username=self.instructor_one.username,
                              password='test')
            response = self.client.post(url, {'emails': 'foo@example.com'})
            self.assertEqual(len(mail.outbox), 2)
            self.assertTrue(CourseInvitation.objects.count() == 1)

    def test_email_invite_no_user(self):
        url = reverse('course-roster-invite-email')
        self.client.login(username=self.instructor_one.username,
                          password='test')
        self.switch_course(self.client, self.sample_course)
        response = self.client.post(url, {})

        self.assertEquals(response.status_code, 302)
        self.assertTrue(
            'Please enter a comma-separated list of email addresses.'
            in response.cookies['messages'].value)

    def test_email_invite_invalid_email(self):
        url = reverse('course-roster-invite-email')
        self.client.login(username=self.instructor_one.username,
                          password='test')
        self.switch_course(self.client, self.sample_course)
        response = self.client.post(url, {'emails': '#$%^,foo@example.com'})

        self.assertEquals(response.status_code, 302)
        self.assertTrue(
            '#$%^ is not a valid email address.'
            in response.cookies['messages'].value)
        self.assertTrue('foo@example.com was invited to join the course'
                        in response.cookies['messages'].value)

    def test_accept_invite_invalid_uuid(self):
        # no uuid
        url = reverse('course-invite-accept', kwargs={'uidb64': None})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 404)

        # already accepted invitation
        invite = CourseInvitationFactory(
            course=self.sample_course, accepted_at=datetime.now(),
            invited_by=self.instructor_one)
        url = reverse('course-invite-accept', kwargs={'uidb64': invite.uuid})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        self.assertTrue(
            'This invitation has already been accepted' in response.content)

    def test_accept_invite_get_invite(self):
        view = CourseAcceptInvitationView()
        self.assertIsNone(view.get_invite(None))

        view = CourseAcceptInvitationView()
        self.assertIsNone(view.get_invite('@#$%^&'))

        invite = CourseInvitationFactory(
            course=self.sample_course, invited_by=self.instructor_one)
        self.assertEquals(view.get_invite(invite.uuid), invite)

    def test_accept_invite_form_valid(self):
        form = AcceptInvitationForm()
        form.cleaned_data = {
            'first_name': 'Foo', 'last_name': 'Bar',
            'password1': 'test', 'password2': 'test',
            'username': 'testname'}

        invite = CourseInvitationFactory(
            course=self.sample_course, invited_by=self.instructor_one)

        view = CourseAcceptInvitationView()
        view.kwargs = {'uidb64': invite.uuid}
        view.form_valid(form)

        user = User.objects.get(username='testname')
        self.assertEquals(user.first_name, 'Foo')
        self.assertEquals(user.last_name, 'Bar')
        self.assertEquals(user.email, invite.email)

        invite.refresh_from_db()
        self.assertTrue(invite.accepted())
        self.assertTrue(invite.accepted_user, user)
        self.assertTrue(self.sample_course.is_member(user))

        self.assertTrue(
            self.client.login(username='testname', password='test'))

    def test_resend_invite(self):
        url = reverse('course-roster-resend-email')
        self.client.login(username=self.instructor_one.username,
                          password='test')
        self.switch_course(self.client, self.sample_course)
        response = self.client.post(url, {'invite-id': '3'})
        self.assertEquals(response.status_code, 404)

        invite = CourseInvitationFactory(
            course=self.sample_course, invited_by=self.instructor_one)

        with self.settings(SERVER_EMAIL='mediathread@example.com'):
            response = self.client.post(url, {'invite-id': invite.id})
            self.assertEquals(response.status_code, 302)

            msg = 'A course invitation was resent to {}'.format(invite.email)
            self.assertTrue(msg in response.cookies['messages'].value)

            self.assertEqual(len(mail.outbox), 1)
            self.assertEqual(mail.outbox[0].subject,
                             'Mediathread Course Invitation: Sample Course')
            self.assertEquals(mail.outbox[0].from_email,
                              'mediathread@example.com')
            self.assertTrue(mail.outbox[0].to, [invite.email])


class MethCourseListAnonViewTest(TestCase):
    def test_get(self):
        url = reverse('course_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)


@freeze_time('2016-05-11')
@override_settings(COURSEAFFILS_COURSESTRING_MAPPER=CourseStringMapper)
class MethCourseListViewTest(LoggedInUserTestMixin, TestCase):
    def setUp(self):
        super(MethCourseListViewTest, self).setUp()

    def test_get_without_featureflag(self):
        url = reverse('course_list')
        with override_flag('course_activation', active=False):
            response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Course Selection')
        self.assertEqual(len(response.context['object_list']), 0)
        with self.assertRaises(KeyError):
            response.context['activatable_affils']

    def test_get_no_affils(self):
        url = reverse('course_list')
        with override_flag('course_activation', active=True):
            response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Course Selection')
        self.assertEqual(len(response.context['object_list']), 0)
        self.assertEqual(len(response.context['activatable_affils']), 0)

    def test_get(self):
        url = reverse('course_list')
        affil_name = 't1.y2016.s001.cf1000.scnc.fc.course:columbia.edu'
        aa = AffilFactory(user=self.u, name=affil_name)
        with override_flag('course_activation', active=True):
            response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Course Selection')
        self.assertContains(response, aa.coursedirectory_name)
        self.assertEqual(len(response.context['object_list']), 0)
        self.assertEqual(len(response.context['activatable_affils']), 1)
        self.assertEqual(response.context['activatable_affils'][0], aa)

    def test_get_past_affil(self):
        url = reverse('course_list')
        affil_name = 't1.y2015.s001.cf1000.scnc.fc.course:columbia.edu'
        aa = AffilFactory(user=self.u, name=affil_name)
        with override_flag('course_activation', active=True):
            response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Course Selection')
        self.assertNotContains(response, aa.coursedirectory_name)
        self.assertEqual(len(response.context['object_list']), 0)
        self.assertEqual(len(response.context['activatable_affils']), 1)
        self.assertEqual(response.context['activatable_affils'][0], aa)

    def test_get_future(self):
        url = reverse('course_list') + '?semester_view=future'
        affil_name = 't3.y2016.s001.cf1000.scnc.fc.course:columbia.edu'
        aa = AffilFactory(user=self.u, name=affil_name)
        with override_flag('course_activation', active=True):
            response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Course Selection')
        self.assertContains(response, aa.coursedirectory_name)
        self.assertEqual(len(response.context['object_list']), 0)
        self.assertEqual(len(response.context['activatable_affils']), 1)
        self.assertEqual(response.context['activatable_affils'][0], aa)


@override_settings(COURSEAFFILS_COURSESTRING_MAPPER=CourseStringMapper)
class AffilActivateViewTest(LoggedInUserTestMixin, TestCase):
    def setUp(self):
        super(AffilActivateViewTest, self).setUp()
        self.aa = AffilFactory(user=self.u)

    def test_get(self):
        response = self.client.get(reverse('affil_activate', kwargs={
            'pk': self.aa.pk
        }))
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            'Course Activation: {}'.format(self.aa.coursedirectory_name))
        self.assertEqual(
            response.context['affil_shortname'],
            self.aa.to_dict()['dept'].upper() +
            self.aa.to_dict()['number'])
        self.assertEqual(response.context['affil'], self.aa)

    def test_post_no_course_name(self):
        self.assertFalse(self.aa.activated)
        response = self.client.post(
            reverse('affil_activate', kwargs={'pk': self.aa.pk}), {
                'affil': self.aa.pk,
                'course_name': '',
                'consult_or_demo': 'consultation',
            })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'This field is required')
        self.assertEqual(Course.objects.count(), 0)

    def test_post(self):
        self.assertFalse(self.aa.activated)
        response = self.client.post(
            reverse('affil_activate', kwargs={'pk': self.aa.pk}), {
                'affil': self.aa.pk,
                'course_name': 'My Course',
                'consult_or_demo': 'consultation',
            })
        self.assertEqual(response.status_code, 302)
        self.aa.refresh_from_db()
        self.assertTrue(self.aa.activated)

        course = Course.objects.last()
        shortname = self.aa.to_dict().get('dept').upper() + \
            self.aa.to_dict().get('number')
        self.assertEqual(course.title, '%s My Course' % shortname)
        self.assertEqual(
            unicode(course.info),
            '%s My Course (Spring 2016) None None-None' % shortname)
        self.assertEqual(course.info.term, 1)
        self.assertEqual(course.info.year, 2016)
        self.assertEqual(Affil.objects.count(), 1)

        self.assertTrue(course.is_faculty(self.u))

    def test_send_faculty_email(self):
        form = CourseActivateForm({
            'affil': self.aa.pk,
            'course_name': 'My Course',
            'consult_or_demo': 'consultation',
        })
        self.assertTrue(form.is_valid())
        AffilActivateView.send_faculty_email(form, self.u)
        self.assertEqual(len(mail.outbox), 1)

        shortname = self.aa.to_dict().get('dept').upper() + \
            self.aa.to_dict().get('number')
        self.assertEqual(
            mail.outbox[0].subject,
            'Your Mediathread Course Activation: %s My Course' % shortname)
        self.assertEquals(
            mail.outbox[0].from_email,
            settings.SERVER_EMAIL)
        self.assertEquals(
            mail.outbox[0].to,
            ['test_user@example.com'])

    def test_send_staff_email(self):
        form = CourseActivateForm({
            'affil': self.aa.pk,
            'course_name': 'My Course',
            'consult_or_demo': 'consultation',
        })
        self.assertTrue(form.is_valid())
        AffilActivateView.send_staff_email(form, self.u)
        self.assertEqual(len(mail.outbox), 1)
        shortname = self.aa.to_dict().get('dept').upper() + \
            self.aa.to_dict().get('number')
        self.assertEqual(
            mail.outbox[0].subject,
            'Mediathread Course Activated: %s My Course' % shortname)
        self.assertEquals(
            mail.outbox[0].from_email,
            'test_user@example.com')
        self.assertEquals(
            mail.outbox[0].to,
            [settings.SERVER_EMAIL])


class CourseInstructorDashboardViewTest(LoggedInUserTestMixin, TestCase):
    def setUp(self):
        super(CourseInstructorDashboardViewTest, self).setUp()
        self.course = CourseFactory()

    def test_get(self):
        response = self.client.get(reverse(
            'course-instructor-dashboard', kwargs={
                'pk': self.course.pk
            }))
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            'Instructor Dashboard: {}'.format(self.course.title))
        self.assertEqual(response.context['object'], self.course)
