from datetime import datetime

from django.test.client import RequestFactory
from django.test.testcases import TestCase

from mediathread.assetmgr.models import Asset
from mediathread.factories import MediathreadTestMixin, ProjectFactory, \
    AssetFactory, AssignmentItemFactory, SherdNoteFactory, ProjectNoteFactory
from mediathread.mixins import RestrictedMaterialsMixin
from mediathread.projects.models import RESPONSE_VIEW_NEVER, \
    RESPONSE_VIEW_SUBMITTED, PUBLISH_WHOLE_CLASS


class RestrictedMaterialsMixinTest(MediathreadTestMixin, TestCase):

    def setUp(self):
        self.setup_sample_course()

        self.assignment = ProjectFactory.create(
            course=self.sample_course, author=self.instructor_one,
            policy=PUBLISH_WHOLE_CLASS[0],
            project_type='selection-assignment')

        self.asset = AssetFactory.create(course=self.sample_course,
                                         primary_source='image')
        self.assets = Asset.objects.filter(id=self.asset.id)

        AssignmentItemFactory.create(project=self.assignment, asset=self.asset)

        self.response_one = ProjectFactory.create(
            course=self.sample_course, author=self.student_one,
            policy='PrivateEditorsAreOwners', parent=self.assignment)
        self.note_one = SherdNoteFactory(
            asset=self.asset, author=self.student_one,
            body='student one selection note', range1=0, range2=1)
        ProjectNoteFactory(project=self.response_one, annotation=self.note_one)

        self.response_two = ProjectFactory.create(
            course=self.sample_course, author=self.student_two,
            policy='PrivateEditorsAreOwners', parent=self.assignment)
        self.note_two = SherdNoteFactory(
            asset=self.asset, author=self.student_one,
            body='student one selection note', range1=0, range2=1)
        ProjectNoteFactory(project=self.response_two, annotation=self.note_two)

        self.mixin = RestrictedMaterialsMixin()
        self.mixin.request = RequestFactory().get('/')
        self.mixin.request.course = self.sample_course

    def assert_visible_notes(self, viewer, expected_notes):
        self.mixin.request.user = viewer
        self.mixin.initialize()
        (assets, notes) = \
            self.mixin.visible_assets_and_notes(self.mixin.request,
                                                self.assets)

        self.assertEquals(notes.count(), len(expected_notes))
        for n in expected_notes:
            self.assertTrue(n in notes)

    def test_visible_assets_and_notes(self):
        self.assert_visible_notes(self.student_one, [self.note_one])
        self.assert_visible_notes(self.student_two, [self.note_two])
        self.assert_visible_notes(self.instructor_one, [])

        # submit student one's response
        self.response_one.create_or_update_collaboration(
            PUBLISH_WHOLE_CLASS[0])
        self.response_one.date_submitted = datetime.now()
        self.response_one.save()

        self.assert_visible_notes(self.student_one, [self.note_one])
        self.assert_visible_notes(self.student_two,
                                  [self.note_one, self.note_two])
        self.assert_visible_notes(self.instructor_one, [self.note_one])

        # change assignment policy to never
        self.assignment.response_view_policy = RESPONSE_VIEW_NEVER[0]
        self.assignment.save()

        self.assert_visible_notes(self.student_one, [self.note_one])
        self.assert_visible_notes(self.student_two, [self.note_two])
        self.assert_visible_notes(self.instructor_one, [self.note_one])

        # change assignment policy to submitted
        self.assignment.response_view_policy = RESPONSE_VIEW_SUBMITTED[0]
        self.assignment.save()
        self.assert_visible_notes(self.student_one, [self.note_one])
        self.assert_visible_notes(self.student_two, [self.note_two])
        self.assert_visible_notes(self.instructor_one, [self.note_one])

        # submit student two's response
        self.response_two.create_or_update_collaboration(
            PUBLISH_WHOLE_CLASS[0])
        self.response_two.date_submitted = datetime.now()
        self.response_two.save()
        self.assert_visible_notes(self.student_one,
                                  [self.note_one, self.note_two])
        self.assert_visible_notes(self.student_two,
                                  [self.note_one, self.note_two])
        self.assert_visible_notes(self.instructor_one,
                                  [self.note_one, self.note_two])
