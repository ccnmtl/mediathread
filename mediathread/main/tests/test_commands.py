from django.test.testcases import TestCase

from mediathread.assetmgr.models import Asset
from mediathread.djangosherd.models import SherdNote
from mediathread.factories import MediathreadTestMixin, UserFactory, \
    AssetFactory, SherdNoteFactory, CourseFactory, ProjectFactory
from mediathread.main.management.commands import clear_guest_sandbox
from mediathread.projects.models import Project


class ClearGuestSandboxTest(MediathreadTestMixin, TestCase):

    def setUp(self):
        # sandbox course
        self.sandbox_course = CourseFactory(title="Mediathread Guest Sandbox")
        self.sandbox_instructor = UserFactory(username='sandbox_instructor')
        self.sandbox_student = UserFactory(username='sandbox_student')

        self.add_as_student(self.sandbox_course, self.sandbox_student)
        self.add_as_faculty(self.sandbox_course, self.sandbox_instructor)

        self.sandbox_asset_instructor = AssetFactory.create(
            course=self.sandbox_course, author=self.sandbox_instructor,
            primary_source='image')

        self.sandbox_note_instructor = SherdNoteFactory(
            asset=self.sandbox_asset_instructor,
            author=self.sandbox_instructor)
        self.sandbox_note_student = SherdNoteFactory(
            asset=self.sandbox_asset_instructor, author=self.sandbox_student)

        self.sandbox_asset_student = AssetFactory.create(
            course=self.sandbox_course, author=self.sandbox_student,
            primary_source='image')

        self.sandbox_project_instructor = ProjectFactory.create(
            course=self.sandbox_course, author=self.sandbox_instructor,
            policy='PrivateEditorsAreOwners')
        self.sandbox_project_student = ProjectFactory.create(
            course=self.sandbox_course, author=self.sandbox_student,
            policy='PrivateEditorsAreOwners')

        # sample course
        self.setup_sample_course()
        self.add_as_faculty(self.sample_course, self.sandbox_instructor)
        sample_asset = AssetFactory.create(
            course=self.sample_course, author=self.sandbox_instructor,
            primary_source='image')
        SherdNote.objects.global_annotation(
            sample_asset, self.sandbox_instructor, auto_create=True)
        ProjectFactory.create(
            course=self.sample_course, author=self.sandbox_instructor,
            policy='PrivateEditorsAreOwners')

    def test_clear_sandbox(self):
        cmd = clear_guest_sandbox.Command()
        opts = {}

        cmd.handle(*opts, **opts)

        # sample course assets, notes & projects are intact
        assets = Asset.objects.filter(course=self.sample_course)
        self.assertEquals(1, assets.count())
        notes = SherdNote.objects.filter(asset__course=self.sample_course)
        self.assertEquals(1, notes.count())
        projects = Project.objects.filter(course=self.sample_course)
        self.assertEquals(1, projects.count())

        # sandbox course - only the sandbox_instructor stuff is still there
        assets = Asset.objects.filter(course=self.sandbox_course)
        notes = SherdNote.objects.filter(asset__course=self.sandbox_course)
        projects = Project.objects.filter(course=self.sandbox_course)
        self.assertEquals(1, assets.count())
        self.assertEquals(1, notes.count())
        self.assertEquals(1, projects.count())
