# coding: utf-8
# pylint: disable-msg=R0904
# pylint: disable-msg=E1103
from __future__ import unicode_literals

from datetime import datetime
import json
import re
import uuid

from courseaffils.columbia import CourseStringMapper
from courseaffils.lib import get_public_name
from courseaffils.models import Affil, Course
from courseaffils.tests.factories import AffilFactory, CourseFactory
from django.conf import settings
from django.contrib.auth.models import User, AnonymousUser, Group
from django.contrib.contenttypes.models import ContentType
from django.core import mail
from django.core.cache import cache
from django.urls import reverse
from django.http.response import Http404
from django.test import TestCase, override_settings
from django.test.client import RequestFactory
from django.utils.encoding import smart_text
from django.utils.html import escape
from django.utils.text import slugify
import factory
from freezegun import freeze_time
from threadedcomments.models import ThreadedComment

from lti_auth.models import LTICourseContext
from lti_auth.tests.factories import LTICourseContextFactory
from mediathread.assetmgr.models import Asset
from mediathread.discussions.utils import get_course_discussions
from mediathread.djangosherd.models import SherdNote
from mediathread.factories import (
    UserFactory, UserProfileFactory, MediathreadTestMixin,
    AssetFactory, ProjectFactory, SherdNoteFactory,
    CourseInvitationFactory)
from mediathread.main import course_details
from mediathread.main.course_details import (
    allow_public_compositions,
    course_information_title,
    all_items_are_visible, all_selections_are_visible, allow_item_download)
from mediathread.main.forms import (
    ContactUsForm, CourseActivateForm, AcceptInvitationForm)
from mediathread.main.models import CourseInvitation
from mediathread.main.tests.mixins import (
    LoggedInUserTestMixin, LoggedInSuperuserTestMixin
)
from mediathread.main.views import (
    AffilActivateView,
    MigrateCourseView, ContactUsView, CourseManageSourcesView,
    CourseRosterView, CourseAddUserByUNIView, CourseAcceptInvitationView,
    unis_list, CourseConvertMaterialsView)
from mediathread.projects.models import Project
from structuredcollaboration.models import Collaboration


class SimpleViewTest(TestCase):
    def test_index(self):
        # Mediathread splash page should appear
        response = self.client.get('/')
        self.assertEquals(response.status_code, 200)

    def test_500(self):
        with self.assertRaises(Exception):
            self.client.get('/500')

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
        response = self.client.get(
            reverse('dashboard-migrate', args=[self.sample_course.pk]))
        self.assertEquals(response.status_code, 403)

    def test_not_logged_in(self):
        response = self.client.get(
            reverse('dashboard-migrate', args=[self.sample_course.pk]))
        self.assertEquals(response.status_code, 302)

    def test_get_context_data(self):
        request = RequestFactory().get(
            reverse('dashboard-migrate', args=[self.sample_course.pk]))
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

        request = RequestFactory().post(
            reverse('dashboard-migrate', args=[self.sample_course.pk]),
            data)
        request.user = self.superuser
        request.course = self.sample_course

        view = MigrateCourseView()
        view.request = request

        self.assertRaises(Http404, view.post, request, self.sample_course.pk)

    def test_post_on_behalf_of_student(self):
        data = {
            'fromCourse': self.alt_course.id,
            'on_behalf_of': self.alt_student.id
        }

        request = RequestFactory().post(
            reverse('dashboard-migrate', args=[self.sample_course.pk]),
            data)
        request.user = self.superuser
        request.course = self.sample_course

        view = MigrateCourseView()
        view.request = request
        response = view.post(request, self.sample_course.pk)

        the_json = json.loads(response.content)
        self.assertFalse(the_json['success'])

    def test_post_on_behalf_of_faculty(self):
        data = {
            'fromCourse': self.alt_course.id,
            'on_behalf_of': self.alt_instructor.id
        }

        request = RequestFactory().post(
            reverse('dashboard-migrate', args=[self.sample_course.pk]),
            data)
        request.user = self.superuser
        request.course = self.sample_course

        view = MigrateCourseView()
        view.request = request
        response = view.post(request, self.sample_course.pk)

        the_json = json.loads(response.content)
        self.assertFalse(the_json['success'])

    def test_migrate_asset(self):
        data = {'fromCourse': self.sample_course.id,
                'asset_ids[]': [self.asset1.id],
                'project_ids[]': []}

        # Migrate assets from SampleCourse into Alternate Course
        # test_instructor_three is a member of both courses
        request = RequestFactory().post(
            reverse('dashboard-migrate', args=[self.sample_course.pk]),
            data)
        request.user = self.instructor_three
        request.course = self.alt_course

        view = MigrateCourseView()
        view.request = request
        response = view.post(request, self.sample_course.pk)

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
        request = RequestFactory().post(
            reverse('dashboard-migrate', args=[self.sample_course.pk]),
            data)
        request.user = self.instructor_three
        request.course = self.alt_course

        view = MigrateCourseView()
        view.request = request
        view.post(request, self.sample_course.pk)

        new_asset = Asset.objects.get(course=self.alt_course,
                                      title=self.asset1.title)
        self.assertEquals(new_asset.sherdnote_set.count(), 2)

        note = new_asset.sherdnote_set.get(title=self.instructor_note.title)
        self.assertEquals(note.tags, self.instructor_note.tags)
        self.assertIsNone(note.body)

        note = new_asset.global_annotation(self.instructor_three, False)
        self.assertEquals(
            note.tags,
            ',image, instructor_one_global,,instructor_two_global,')
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
        request = RequestFactory().post(
            reverse('dashboard-migrate', args=[self.sample_course.pk]),
            data)
        request.user = self.instructor_three
        request.course = self.alt_course

        view = MigrateCourseView()
        view.request = request
        view.post(request, self.sample_course.pk)

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
            'instructor one global noteinstructor two global note')

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
        request = RequestFactory().post(
            reverse('dashboard-migrate', args=[self.sample_course.pk]),
            data)
        request.user = self.instructor_three
        request.course = self.alt_course

        view = MigrateCourseView()
        view.request = request
        view.post(request, self.sample_course.pk)

        new_asset = Asset.objects.get(course=self.alt_course,
                                      title=self.asset1.title)
        self.assertEquals(new_asset.sherdnote_set.count(), 2)

        note = new_asset.sherdnote_set.get(title=self.instructor_note.title)
        self.assertEquals(note.tags, self.instructor_note.tags)
        self.assertEquals(note.body, self.instructor_note.body)

        note = new_asset.global_annotation(self.instructor_three, False)
        self.assertEquals(
            note.tags,
            ',image, instructor_one_global,,instructor_two_global,')
        self.assertEquals(
            note.body,
            'instructor one global noteinstructor two global note')

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
        request = RequestFactory().post(
            reverse('dashboard-migrate', args=[self.sample_course.pk]),
            data)
        request.user = self.instructor_three
        request.course = self.alt_course

        view = MigrateCourseView()
        view.request = request
        response = view.post(request, self.sample_course.pk)

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
        flv = AssetFactory.create(course=self.sample_course,
                                  primary_source='flv_pseudo')
        SherdNoteFactory(asset=flv, author=self.instructor_one)

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
                              settings.SERVER_EMAIL)
            self.assertEquals(mail.outbox[0].to,
                              [settings.SUPPORT_DESTINATION])


class CourseManageSourcesViewTest(MediathreadTestMixin, TestCase):

    def setUp(self):
        self.setup_sample_course()
        self.enable_upload(self.sample_course)
        self.superuser = UserFactory(is_staff=True, is_superuser=True)

    def test_not_logged_in(self):
        response = self.client.get(
            reverse('course-manage-sources', args=[self.sample_course.pk]))
        self.assertEquals(response.status_code, 302)

    def test_as_student(self):
        self.assertTrue(
            self.client.login(username=self.student_one.username,
                              password='test'))
        response = self.client.get(
            reverse('course-manage-sources', args=[self.sample_course.pk]))
        self.assertEquals(response.status_code, 403)

    def test_get_context(self):
        request = RequestFactory().get(
            reverse('course-manage-sources', args=[self.sample_course.pk]))
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

        self.client.post(
            reverse('course-manage-sources', args=[self.sample_course.pk]),
            data)
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
        url = reverse('course-delete-materials', args=[self.sample_course.pk])
        data = {'clear_all': True, 'username': self.student_one.username}

        self.client.login(username=self.student_one.username, password='test')
        response = self.client.post(url, data)
        self.assertEquals(response.status_code, 302)

    def test_clear_all(self):
        url = reverse('course-delete-materials', args=[self.sample_course.pk])
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

        self.assertTrue(
            Course.objects.filter(title='Sample Course').exists())

    def test_clear_student_only(self):
        url = reverse('course-delete-materials', args=[self.sample_course.pk])
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

        self.assertTrue(
            Course.objects.filter(title='Sample Course').exists())

    def test_clear_and_delete_course(self):
        url = reverse('course-delete-materials', args=[self.sample_course.pk])
        data = {
            'clear_all': True,
            'username': self.superuser.username,
            'delete-course': 'Permanently Delete Course'}

        self.client.login(username=self.superuser.username, password='test')
        self.switch_course(self.client, self.sample_course)

        response = self.client.post(url, data)
        self.assertEquals(response.status_code, 302)
        self.assertTrue('Sample Course and requested materials were deleted'
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
        self.assertFalse(
            Course.objects.filter(title='Sample Course').exists())


class CourseRosterViewsTest(MediathreadTestMixin, TestCase):

    def setUp(self):
        self.setup_sample_course()
        self.url = reverse('course-roster', args=[self.sample_course.pk])

    def test_validate_uni(self):
        view = CourseAddUserByUNIView()
        self.assertTrue(view.validate_uni('abc123'))
        self.assertTrue(view.validate_uni('ab4567'))
        self.assertFalse(view.validate_uni('alpha'))
        self.assertFalse(view.validate_uni('alpha@columbia.edu'))

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

        response = self.client.post(
            url, {'unis': ' abc123 ,efg456,az4@columbia.edu,1234 56'})
        self.assertEquals(response.status_code, 302)

        user = User.objects.get(username='efg456')
        self.assertTrue(self.sample_course.is_true_member(user))
        user = User.objects.get(username='abc123')
        self.assertTrue(self.sample_course.is_true_member(user))

        self.assertTrue('John Smith (abc123) is already a course member'
                        in response.cookies['messages'].value)
        self.assertTrue('efg456 is now a course member'
                        in response.cookies['messages'].value)
        self.assertTrue('az4@columbia.edu is not a valid UNI'
                        in response.cookies['messages'].value)
        self.assertTrue('1234 is not a valid UNI'
                        in response.cookies['messages'].value)
        self.assertTrue('56 is not a valid UNI'
                        in response.cookies['messages'].value)

    def test_uni_invite_post_newlines(self):
        self.client.login(username=self.instructor_one.username,
                          password='test')
        self.switch_course(self.client, self.sample_course)

        url = reverse('course-roster-add-uni')
        # sometimes they enter a newline instead of a comma
        response = self.client.post(url, {'unis': ' abc123\nefg456,'})
        self.assertEquals(response.status_code, 302)

        user = User.objects.get(username='efg456')
        self.assertTrue(self.sample_course.is_true_member(user))
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
            self.assertTrue(
                'An email was sent to foo@example.com inviting this user to '
                'join the course.' in response.cookies['messages'].value)

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
        self.assertTrue(
            'An email was sent to foo@example.com inviting '
            'this user to join the course.'
            in response.cookies['messages'].value)

    def test_accept_invite_invalid_uuid(self):
        # random new uuid
        url = reverse(
            'course-invite-accept',
            kwargs={'uidb64': uuid.uuid4()})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 404)

        # already accepted invitation
        invite = CourseInvitationFactory(
            course=self.sample_course, accepted_at=datetime.now(),
            invited_by=self.instructor_one)
        url = reverse('course-invite-accept', kwargs={'uidb64': invite.uuid})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        self.assertContains(
            response, 'This invitation has already been accepted')

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


class UnisListTest(TestCase):
    def test_commas(self):
        self.assertEqual(unis_list("foo,bar"), ["foo", "bar"])

    def test_whitespace(self):
        self.assertEqual(unis_list("\tfoo,   bar, \n"), ["foo", "bar"])

    def test_newlines(self):
        self.assertEqual(unis_list("foo\nbar\n\rbaz"), ["foo", "bar", "baz"])


class MethCourseListAnonViewTest(TestCase):
    def test_get(self):
        url = reverse('course_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)


@freeze_time('2016-05-11')
@override_settings(COURSEAFFILS_COURSESTRING_MAPPER=CourseStringMapper)
class MethCourseListViewTest(LoggedInUserTestMixin, TestCase):
    def test_get_no_affils(self):
        url = reverse('course_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'My Courses')
        self.assertEqual(len(response.context['object_list']), 0)
        self.assertEqual(len(response.context['activatable_affils']), 0)

    def test_get(self):
        url = reverse('course_list')
        affil_name = 't1.y2016.s001.cf1000.scnc.fc.course:columbia.edu'
        aa = AffilFactory(user=self.u, name=affil_name)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'My Courses')
        self.assertContains(response, aa.coursedirectory_name)
        self.assertEqual(len(response.context['object_list']), 0)
        self.assertEqual(len(response.context['activatable_affils']), 1)
        self.assertEqual(response.context['activatable_affils'][0], aa)

    def test_get_past_affil(self):
        url = reverse('course_list')
        affil_name = 't1.y2015.s001.cf1000.scnc.fc.course:columbia.edu'
        aa = AffilFactory(user=self.u, name=affil_name)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'My Courses')
        self.assertNotContains(response, aa.coursedirectory_name)
        self.assertEqual(len(response.context['object_list']), 0)
        self.assertEqual(len(response.context['activatable_affils']), 1)
        self.assertEqual(response.context['activatable_affils'][0], aa)

    def test_get_future(self):
        url = reverse('course_list') + '?semester_view=future'
        affil_name = 't3.y2016.s001.cf1000.scnc.fc.course:columbia.edu'
        aa = AffilFactory(user=self.u, name=affil_name)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'My Courses')
        self.assertContains(response, aa.coursedirectory_name)
        self.assertEqual(len(response.context['object_list']), 0)
        self.assertEqual(len(response.context['activatable_affils']), 1)
        self.assertEqual(response.context['activatable_affils'][0], aa)


@freeze_time('2015-10-11')
@override_settings(COURSEAFFILS_COURSESTRING_MAPPER=CourseStringMapper)
@override_settings(
    TASK_ASSIGNMENT_DESTINATION='https://pmt.ctl.columbia.edu/drf/'
    'external_add_item/')
@override_settings(MEDIATHREAD_PMT_MILESTONE_ID=12)
@override_settings(MEDIATHREAD_PMT_OWNER_USERNAME='pmt_user')
class AffilActivateViewTest(LoggedInUserTestMixin, TestCase):
    def setUp(self):
        super(AffilActivateViewTest, self).setUp()
        self.aa = AffilFactory(
            name=factory.Sequence(
                lambda n:
                't1.y2016.s001.cf100%d.scnc.fc.course:columbia.edu' % n),
            user=self.u)
        self.form_data = {
            'affil': self.aa.pk,
            'course_name': 'English for Cats',
        }

    def test_get(self):
        response = self.client.get(reverse('affil_activate', kwargs={
            'pk': self.aa.pk
        }))
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            'Course Activation: {}'.format(self.aa.coursedirectory_name))
        self.assertEqual(response.context['affil'], self.aa)

    def test_post_no_course_name(self):
        self.assertFalse(self.aa.activated)
        del self.form_data['course_name']
        response = self.client.post(
            reverse('affil_activate', kwargs={'pk': self.aa.pk}),
            self.form_data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'This field is required')
        self.assertEqual(Course.objects.count(), 0)

    def test_post_duplicate_course(self):
        self.u.profile = UserProfileFactory(user=self.u)
        self.u.save()
        self.assertFalse(self.aa.activated)

        studentaffil = re.sub(r'\.fc\.', '.st.', self.aa.name)
        g = Group.objects.create(name=studentaffil)
        fg = Group.objects.create(name=self.aa.name)
        Course.objects.create(
            group=g,
            faculty_group=fg,
            title='Already created')

        response = self.client.post(
            reverse('affil_activate', kwargs={'pk': self.aa.pk}),
            self.form_data,
            follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Course.objects.count(), 1)

    def test_post(self):
        self.u.profile = UserProfileFactory(user=self.u)
        self.u.save()
        self.assertFalse(self.aa.activated)
        request = RequestFactory().get(
            reverse('affil_activate', kwargs={'pk': self.aa.pk}))
        response = self.client.post(
            reverse('affil_activate', kwargs={'pk': self.aa.pk}),
            self.form_data,
            follow=True)
        self.assertEqual(response.status_code, 200)

        self.aa.refresh_from_db()
        self.assertTrue(self.aa.activated)

        course = Course.objects.last()
        self.assertEqual(course.title, 'English for Cats')
        self.assertEqual(
            smart_text(course.info),
            'English for Cats (Spring 2016) None None-None')
        self.assertEqual(course.info.term, 1)
        self.assertEqual(course.info.year, 2016)
        self.assertEqual(Affil.objects.count(), 1)

        self.assertTrue(course.is_true_member(self.u))
        self.assertTrue(course.is_faculty(self.u))
        self.assertEqual(course.get_detail('instructor', None),
                         get_public_name(self.u, request))

        self.assertContains(
            response,
            'You\'ve activated your course.',
            count=1)
        self.assertContains(response, 'English for Cats')
        self.assertContains(response, 'Future Courses')

    def test_send_faculty_email(self):
        form = CourseActivateForm(self.form_data)
        self.assertTrue(form.is_valid())
        AffilActivateView.send_faculty_email(form, self.u)
        self.assertEqual(len(mail.outbox), 1)

        self.assertEqual(
            mail.outbox[0].subject,
            'Your Mediathread Course Activation: English for Cats')
        self.assertEquals(
            mail.outbox[0].from_email,
            settings.SERVER_EMAIL)
        self.assertEquals(
            mail.outbox[0].to,
            ['test_user@example.com'])

    def test_send_staff_email(self):
        self.form_data = {
            'affil': self.aa.pk,
            'course_name': 'English for Cats',
            'date_range_start': datetime(year=2015, month=10, day=1),
            'date_range_end': datetime(year=2015, month=12, day=13),
            'request_consult_or_demo': ['demo'],
            'how_will_mediathread_improve_your_class': 'Just because!',
            'hear_about_mediathread': 'recommendation_colleague',
            'used_mediathread': 'yes',
        }
        form = CourseActivateForm(self.form_data)
        self.assertTrue(form.is_valid())
        AffilActivateView.send_staff_email(form, self.u)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(
            mail.outbox[0].subject,
            'Mediathread Course Activated: English for Cats')
        self.assertEquals(
            mail.outbox[0].from_email,
            settings.SERVER_EMAIL)
        self.assertEquals(
            mail.outbox[0].to,
            [settings.SERVER_EMAIL])
        self.assertIn(
            'Course Title: {}'.format('English for Cats'),
            mail.outbox[0].body)
        self.assertIn(
            'Date Range: 2015-10-01 - 2015-12-13',
            mail.outbox[0].body)
        self.assertTrue(
            re.search(r'Consult\/Demo request: \[u?\'demo\'\]',
                      mail.outbox[0].body))
        self.assertIn(
            'How will Mediathread be used to improve your class?\n' +
            'Just because!',
            mail.outbox[0].body)
        self.assertIn(
            'How did you hear about Mediathread? recommendation_colleague',
            mail.outbox[0].body)
        self.assertIn(
            'Have you used Mediathread before? yes',
            mail.outbox[0].body)
        self.assertIn(
            'Faculty: {} <{}>'.format('test_user', 'test_user@example.com'),
            mail.outbox[0].body)

    def test_make_pmt_activation_item(self):
        form = CourseActivateForm(self.form_data)
        self.assertTrue(form.is_valid())
        r = AffilActivateView.make_pmt_activation_item(form, self.u)
        self.assertIsNotNone(r)


class InstructorDashboardSettingsViewTest(LoggedInUserTestMixin, TestCase):
    def setUp(self):
        super(InstructorDashboardSettingsViewTest, self).setUp()
        self.course = CourseFactory()
        self.url = reverse(
            'course-settings-general', args=[self.course.pk])

        self.u.groups.add(self.course.group)
        self.u.groups.add(self.course.faculty_group)

        set_course_url = '/?set_course=%s' % self.course.group.name
        self.client.get(set_course_url)

    def test_get(self):
        response = self.client.get(
            reverse('course-settings-general', args=[self.course.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.course.title)
        self.assertContains(response, 'Manage Course')
        self.assertEqual(response.context['object'], self.course)

    def test_post(self):
        response = self.client.post(
            reverse('course-settings-general', args=[self.course.pk]),
            {
                'title': 'New Title',
                'homepage_title': 'new homepage title',
            },
            follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'New Title')
        self.assertContains(response, 'Manage Course')
        self.assertEqual(response.context['object'], self.course)
        self.assertEqual(Course.objects.filter(title='New Title').count(), 1)
        course = Course.objects.get(title='New Title')
        self.assertEqual(allow_public_compositions(course), False)
        self.assertEqual(course_information_title(course),
                         'new homepage title')
        self.assertEqual(all_items_are_visible(course), False)
        self.assertEqual(all_selections_are_visible(course), False)
        self.assertEqual(allow_item_download(course), False)

        response = self.client.post(
            reverse('course-settings-general', args=[self.course.pk]),
            {
                'title': 'New Title',
                'homepage_title': 'new homepage title',
                'publish_to_world': True,
                'see_eachothers_items': True,
                'see_eachothers_selections': True,
                'allow_item_download': True
            },
            follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'New Title')
        self.assertContains(response, 'Manage Course')
        self.assertEqual(response.context['object'], self.course)
        self.assertEqual(Course.objects.filter(title='New Title').count(), 1)
        course = Course.objects.get(title='New Title')
        self.assertEqual(allow_public_compositions(course), True)
        self.assertEqual(course_information_title(course),
                         'new homepage title')
        self.assertEqual(all_items_are_visible(course), True)
        self.assertEqual(all_selections_are_visible(course), True)
        self.assertEqual(allow_item_download(course), True)

        response = self.client.post(
            reverse('course-settings-general', args=[self.course.pk]),
            {
                'title': 'New Title',
                'homepage_title': 'new homepage title',
                'publish_to_world': True,
                'see_eachothers_items': True,
                'see_eachothers_selections': True,
                'allow_item_download': False
            },
            follow=True)

    def test_post_duplicate_title(self):
        # Duplicate titles should be allowed, since it may be the same
        # course in a different term.
        CourseFactory(title='New Title')
        response = self.client.post(
            reverse('course-settings-general', args=[self.course.pk]),
            {
                'title': 'New Title',
                'homepage_title': 'new homepage title',
            },
            follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'New Title')
        self.assertContains(response, 'Manage Course')
        self.assertEqual(response.context['object'], self.course)

        self.assertEqual(Course.objects.filter(title='New Title').count(), 2)
        course = response.context['object']
        self.assertEqual(allow_public_compositions(course), False)
        self.assertEqual(course_information_title(course),
                         'new homepage title')
        self.assertEqual(all_items_are_visible(course), False)
        self.assertEqual(all_selections_are_visible(course), False)

    def test_post_empty_title(self):
        CourseFactory(title='New Title')
        response = self.client.post(
            reverse('course-settings-general', args=[self.course.pk]),
            {
                'title': '     ',
                'homepage_title': 'new homepage title',
            },
            follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.course.title)
        self.assertContains(response, 'Manage Course')
        self.assertFalse(response.context['form'].is_valid())
        self.assertContains(response, escape('Title can\'t be blank.'))
        self.assertEqual(response.context['object'], self.course)

        self.assertEqual(
            Course.objects.filter(title=self.course.title).count(), 1)
        self.assertEqual(Course.objects.filter(title='New Title').count(), 1)
        course = Course.objects.get(title=self.course.title)
        self.assertEqual(allow_public_compositions(course), False)
        self.assertEqual(course_information_title(course),
                         'From Your Instructor')
        self.assertEqual(all_items_are_visible(course), True)
        self.assertEqual(all_selections_are_visible(course), True)

    def test_post_reset(self):
        CourseFactory(title='New Title')
        response = self.client.post(
            reverse('course-settings-general', args=[self.course.pk]), {
                'title': '     ',
                'homepage_title': 'doesnt update',
                'publish_to_world': False,
                'see_eachothers_items': True,
                'see_eachothers_selections': False,
                'reset': True,
            }, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.course.title)
        self.assertContains(response, 'Manage Course')
        self.assertEqual(response.context['object'], self.course)

        self.assertEqual(
            Course.objects.filter(title=self.course.title).count(), 1)
        self.assertEqual(Course.objects.filter(title='New Title').count(), 1)
        course = Course.objects.get(title=self.course.title)
        self.assertEqual(allow_public_compositions(course), False)
        self.assertEqual(course_information_title(course),
                         'From Your Instructor')
        self.assertEqual(all_items_are_visible(course), True)
        self.assertEqual(all_selections_are_visible(course), True)

        response = self.client.post(
            reverse('course-settings-general', args=[self.course.pk]), {
                'title': 'New Title 1',
                'homepage_title': 'updated homepage title',
                'publish_to_world': True,
                'see_eachothers_items': True,
                'see_eachothers_selections': True
            }, follow=True)
        self.assertEqual(response.status_code, 200)
        course.refresh_from_db()
        self.assertEqual(course.title, 'New Title 1')
        self.assertEqual(course_information_title(course),
                         'updated homepage title')

        response = self.client.post(
            reverse('course-settings-general', args=[self.course.pk]), {
                'title': 'New Title',
                'homepage_title': 'doesnt update',
                'publish_to_world': True,
                'see_eachothers_items': True,
                'see_eachothers_selections': True,
                'reset': True,
            }, follow=True)
        self.assertEqual(response.status_code, 200)
        course.refresh_from_db()
        self.assertEqual(course.title, 'New Title 1')
        self.assertEqual(allow_public_compositions(course), False)
        self.assertEqual(course_information_title(course),
                         'From Your Instructor')
        self.assertEqual(all_items_are_visible(course), True)
        self.assertEqual(all_selections_are_visible(course), True)


class LTICourseSelectorTest(MediathreadTestMixin, TestCase):

    def setUp(self):
        self.setup_sample_course()

    def test_get(self):
        ctx = LTICourseContextFactory(
            group=self.sample_course.group,
            faculty_group=self.sample_course.faculty_group)

        url = reverse('lti-course-select', args=[ctx.lms_course_context])

        self.client.login(
            username=self.instructor_one.username, password='test')
        response = self.client.get(url, follow=True)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.context['course'], self.sample_course)


class LTICourseCreateTest(TestCase):

    def test_post_sis_course_id(self):
        with self.settings(
                COURSEAFFILS_COURSESTRING_MAPPER=CourseStringMapper):
            user = UserFactory()
            self.client.login(username=user.username, password='test')

            data = {
                'lms_course': '1234',
                'lms_course_title': 'LTI Course',
                'sis_course_id': 'SOCWT7113_010_2017_3'
            }
            response = self.client.post(reverse('lti-course-create'), data)
            self.assertEqual(response.status_code, 302)

            c = Course.objects.get(title='LTI Course')
            self.assertEquals(
                c.group.name,
                't3.y2017.s010.ct7113.socw.st.course:columbia.edu')
            self.assertEquals(
                c.faculty_group.name,
                't3.y2017.s010.ct7113.socw.fc.course:columbia.edu')

            self.assertEquals(c.info.term, 3)
            self.assertEquals(c.info.year, 2017)

            self.assertTrue(user in c.group.user_set.all())
            self.assertTrue(user in c.faculty_group.user_set.all())

            self.assertEqual(len(mail.outbox), 2)

            self.assertEqual(mail.outbox[0].subject,
                             'Mediathread Course Connected')
            self.assertEquals(mail.outbox[0].from_email,
                              settings.SERVER_EMAIL)
            self.assertEquals(mail.outbox[0].to,
                              [settings.SERVER_EMAIL])

            self.assertEqual(mail.outbox[1].subject,
                             'Mediathread Course Connected')
            self.assertEquals(mail.outbox[1].from_email,
                              settings.SERVER_EMAIL)
            self.assertEquals(mail.outbox[1].to,
                              [user.email])

            LTICourseContext.objects.get(
                lms_course_context='1234',
                group=c.group, faculty_group=c.faculty_group)

            # try this again and make sure there is no duplication
            data['lms_course_title'] = 'LTI Course With More Detail'
            response = self.client.post(reverse('lti-course-create'), data)
            self.assertEqual(response.status_code, 302)
            Course.objects.get(title='LTI Course')
            Group.objects.get(name=c.group.name)
            Group.objects.get(name=c.faculty_group.name)
            LTICourseContext.objects.get(
                lms_course_context='1234',
                group=c.group, faculty_group=c.faculty_group)

    def test_post_course_context(self):
        with self.settings(
                COURSEAFFILS_COURSESTRING_MAPPER=CourseStringMapper):

            user = UserFactory()
            self.client.login(username=user.username, password='test')

            data = {
                'lms_course': '1234',
                'lms_course_title': 'LTI Course',
                'sis_course_id': '20170152049'
            }
            response = self.client.post(reverse('lti-course-create'), data)
            self.assertEqual(response.status_code, 302)

            c = Course.objects.get(title='LTI Course')
            self.assertEquals(c.group.name, '1234')
            self.assertEquals(c.faculty_group.name, '1234_faculty')
            self.assertEquals(c.info.term, 1)
            self.assertEquals(c.info.year, 2017)

            self.assertTrue(user in c.group.user_set.all())
            self.assertTrue(user in c.faculty_group.user_set.all())

            LTICourseContext.objects.get(
                lms_course_context='1234',
                group=c.group, faculty_group=c.faculty_group)

            # try this again and make sure there is no duplication
            data['lms_course_title'] = 'LTI Course With More Detail'
            response = self.client.post(reverse('lti-course-create'), data)
            self.assertEqual(response.status_code, 302)
            Course.objects.get(title='LTI Course')
            Group.objects.get(name=c.group.name)
            Group.objects.get(name=c.faculty_group.name)
            LTICourseContext.objects.get(
                lms_course_context='1234',
                group=c.group, faculty_group=c.faculty_group)

    def test_post_course_context_with_unicode(self):
        with self.settings(
                COURSEAFFILS_COURSESTRING_MAPPER=CourseStringMapper):

            user = UserFactory()
            self.client.login(username=user.username, password='test')

            data = {
                'lms_course': '1234',
                'lms_course_title': 'LTI Course "Película", rødgrød med fløde',
                'sis_course_id': '20170152049'
            }
            response = self.client.post(reverse('lti-course-create'), data)
            self.assertEqual(response.status_code, 302)

            c = Course.objects.get(
                title='LTI Course "Película", rødgrød med fløde')
            self.assertEquals(c.group.name, '1234')
            self.assertEquals(c.faculty_group.name, '1234_faculty')
            self.assertEquals(c.info.term, 1)
            self.assertEquals(c.info.year, 2017)

            self.assertTrue(user in c.group.user_set.all())
            self.assertTrue(user in c.faculty_group.user_set.all())

            LTICourseContext.objects.get(
                lms_course_context='1234',
                group=c.group, faculty_group=c.faculty_group)

            # try this again and make sure there is no duplication
            data['lms_course_title'] = 'LTI Course With More Detail'
            response = self.client.post(reverse('lti-course-create'), data)
            self.assertEqual(response.status_code, 302)
            Course.objects.get(
                title='LTI Course "Película", rødgrød med fløde')
            Group.objects.get(name=c.group.name)
            Group.objects.get(name=c.faculty_group.name)
            LTICourseContext.objects.get(
                lms_course_context='1234',
                group=c.group, faculty_group=c.faculty_group)


class CourseDetailViewAnonTest(TestCase):
    def setUp(self):
        self.course = CourseFactory()

    def test_get(self):
        r = self.client.get(reverse('course_detail', args=(self.course.pk,)))
        self.assertEqual(r.status_code, 302)


class CourseDetailViewTest(LoggedInUserTestMixin, TestCase):
    def setUp(self):
        super(CourseDetailViewTest, self).setUp()
        self.course = CourseFactory()
        Collaboration.objects.get_or_create(
            content_type=ContentType.objects.get_for_model(Course),
            object_pk=self.course.pk, slug=slugify(self.course.title))

    def test_get(self):
        r = self.client.get(reverse('course_detail', args=(self.course.pk,)))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, self.course.title)
        self.assertContains(r, 'Course Non-member')

        # TODO:
        # r = self.client.get(
        #     reverse('course_detail', args=(self.course.pk,)) + 'asset/'
        # )
        # self.assertEqual(r.status_code, 200)
        # self.assertContains(r, self.course.title)


class CourseDetailSuperuserViewTest(LoggedInSuperuserTestMixin, TestCase):
    def setUp(self):
        super(CourseDetailSuperuserViewTest, self).setUp()
        self.course = CourseFactory()
        Collaboration.objects.get_or_create(
            content_type=ContentType.objects.get_for_model(Course),
            object_pk=self.course.pk, slug=slugify(self.course.title))

    def test_get(self):
        r = self.client.get(reverse('course_detail', args=(self.course.pk,)))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, self.course.title)
        self.assertContains(r, 'Course Non-member')


class ConvertMaterialsViewTest(MediathreadTestMixin, TestCase):

    def setUp(self):
        self.setup_sample_course()
        self.setup_sample_assets()
        self.superuser = User.objects.create(username='ccnmtl',
                                             password='test',
                                             is_superuser=True,
                                             is_staff=True)

    def tearDown(self):
        cache.clear()

    def test_get_context_data(self):
        request = RequestFactory().get('/dashboard/convert/')
        request.user = self.superuser
        request.course = self.sample_course

        view = CourseConvertMaterialsView()
        view.request = request

        with self.settings(ASSET_CONVERT_API=None):
            ctx = view.get_context_data()
            self.assertFalse(ctx['endpoint'])
            self.assertEquals(ctx['assets'].count(), 3)

    def test_get_conversion_endpoint(self):
        view = CourseConvertMaterialsView()
        with self.settings(SERVER_ADMIN_SECRETKEYS={}):
            self.assertEquals(view.get_conversion_endpoint(), (None, None))

        rv = ('http://something', 'foo')
        with self.settings(ASSET_CONVERT_API=rv[0],
                           SERVER_ADMIN_SECRETKEYS={rv[0]: rv[1]}):
            self.assertEquals(view.get_conversion_endpoint(), rv)


class CollectionAddViewTest(MediathreadTestMixin, TestCase):

    def setUp(self):
        self.setup_sample_course()
        self.superuser = UserFactory(is_staff=True, is_superuser=True)

    def test_get(self):
        url = reverse('collection-add-view', args=[self.sample_course.id])
        response = self.client.get(url)
        self.assertEquals(response.status_code, 302)

        self.client.login(
            username=self.instructor_one.username, password='test')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.context['request'])
        self.assertEqual(response.context['owners'], [])
        self.assertTrue(response.context['can_upload'])
        self.assertIsNone(response.context['uploader'])
        self.assertIsNotNone(response.context['collections'])

        self.enable_upload(self.sample_course)

        self.superuser.groups.add(self.sample_course.group)
        self.client.login(
            username=self.superuser.username, password='test')
        response = self.client.get(url)
        self.assertIsNotNone(response.context['uploader'])
        self.assertTrue(len(response.context['owners']) > 0)
