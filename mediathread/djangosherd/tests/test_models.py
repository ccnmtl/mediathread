# pylint: disable-msg=R0904
from django.contrib.auth.models import User
from django.test import TestCase
from threadedcomments.models import ThreadedComment

from mediathread.assetmgr.models import Asset
from mediathread.djangosherd.models import SherdNote, DiscussionIndex
from mediathread.factories import AssetFactory, \
    SherdNoteFactory, MediathreadTestMixin, ProjectFactory, \
    AssignmentItemFactory, ProjectNoteFactory
from mediathread.projects.tests.factories import ProjectSequenceAssetFactory
from mediathread.sequence.tests.factories import SequenceAssetFactory, \
    SequenceMediaElementFactory
from mediathread.taxonomy.models import Vocabulary, Term


class SherdNoteTest(MediathreadTestMixin, TestCase):

    def setUp(self):
        self.setup_sample_course()

    def test_is_global_annotation(self):
        asset = AssetFactory(course=self.sample_course)
        global_annotation, created = SherdNote.objects.global_annotation(
            asset, self.student_three, auto_create=True)
        self.assertTrue(global_annotation.is_global_annotation)
        self.assertEqual(global_annotation.display_title(), asset.title)

        whole_item_annotation = SherdNoteFactory(
            asset=asset, author=self.student_three,
            title="Whole Item Selection", range1=0, range2=0)
        self.assertFalse(whole_item_annotation.is_global_annotation)
        self.assertEqual(whole_item_annotation.display_title(),
                         'Whole Item Selection')

        real_annotation = SherdNoteFactory(
            asset=asset, author=self.student_three,
            title="Selection", range1=116.25, range2=6.75)
        self.assertFalse(real_annotation.is_global_annotation)
        self.assertEqual(real_annotation.display_title(), 'Selection')

    def test_seconds_to_code(self):
        self.assertRaises(TypeError, SherdNote.secondsToCode, None)
        self.assertEqual(SherdNote.secondsToCode(0), "0:00")
        self.assertEqual(SherdNote.secondsToCode(5), "0:05")
        self.assertEqual(SherdNote.secondsToCode(60), "01:00")
        self.assertEqual(SherdNote.secondsToCode(120), "02:00")
        self.assertEqual(SherdNote.secondsToCode(3600, True), "01:00:00")
        self.assertEqual(SherdNote.secondsToCode(6400), "01:46:40")
        self.assertEqual(SherdNote.secondsToCode(86400, True), "24:00:00")
        self.assertEqual(SherdNote.secondsToCode(363600, True), "101:00:00")

    def test_range_as_timecode(self):
        asset = AssetFactory(course=self.sample_course)

        global_annotation, created = SherdNote.objects.global_annotation(
            asset, self.student_three, auto_create=True)
        self.assertEqual(global_annotation.range_as_timecode(), "")

        whole_item_annotation = SherdNoteFactory(
            asset=asset, author=self.student_three)
        self.assertEqual(whole_item_annotation.range_as_timecode(), "")

        real_annotation = SherdNoteFactory(
            asset=asset, author=self.student_three, range1=28, range2=39)
        self.assertEqual(real_annotation.range_as_timecode(), "0:28 - 0:39")

        real_annotation = SherdNoteFactory(
            asset=asset, author=self.student_three, range1=43, range2=75)
        self.assertEqual(real_annotation.range_as_timecode(), "0:43 - 01:15")

    def test_get_global_annotation(self):
        asset = AssetFactory(course=self.sample_course)
        author = self.instructor_one

        ann, created = SherdNote.objects.global_annotation(asset, author)
        self.assertTrue(created)

        ann, created = SherdNote.objects.global_annotation(asset, author)
        self.assertFalse(created)

        self.assertEqual(ann.title, None)
        self.assertEqual(ann.title, None)
        self.assertEqual(ann.body, None)
        self.assertEqual(ann.tags, '')

        author = self.student_one
        ann, created = SherdNote.objects.global_annotation(asset, author)
        self.assertTrue(created)
        self.assertEqual(ann.title, None)
        self.assertEqual(ann.body, None)
        self.assertEqual(ann.tags, '')

    def test_tags_split(self):
        asset = AssetFactory(course=self.sample_course)
        ann, created = SherdNote.objects.global_annotation(
            asset, self.instructor_one)

        # no tags
        tags = ann.tags_split()
        self.assertEqual(len(tags), 0)

        # one tag
        ann.tags = ',foobar'
        ann.save()
        tags = ann.tags_split()
        self.assertEqual(len(tags), 1)
        self.assertEqual(tags[0].name, 'foobar')

        # two tags
        ann.tags = ',youtube, test_instructor_item'
        ann.save()
        tags = ann.tags_split()
        self.assertEqual(len(tags), 2)
        self.assertEqual(tags[0].name, 'test_instructor_item')
        self.assertEqual(tags[1].name, 'youtube')

    def test_add_tag(self):
        asset = AssetFactory(course=self.sample_course)
        ann, created = SherdNote.objects.global_annotation(
            asset, self.instructor_one)

        ann.tags = ',foobar'
        ann.save()

        ann.add_tag("foo")
        ann.add_tag("bar")
        ann.save()

        tags = ann.tags_split()
        self.assertEqual(len(tags), 3)
        self.assertEqual(tags[0].name, 'bar')
        self.assertEqual(tags[1].name, 'foo')
        self.assertEqual(tags[2].name, 'foobar')

    def test_update_reference_in_string(self):
        old_asset = AssetFactory(course=self.sample_course,
                                 author=self.student_one)
        old_note = SherdNoteFactory(
            asset=old_asset, author=self.student_one,
            title="Selection", range1=43, range2=75)
        alt_note = SherdNoteFactory(
            asset=old_asset, author=self.student_one,
            title="Alt Selection", range1=43, range2=75)

        new_asset = AssetFactory(course=self.sample_course,
                                 author=self.student_one)
        new_note = SherdNoteFactory(
            asset=new_asset, author=self.student_one,
            title="Selection", range1=43, range2=75)

        text = ('<p><a href="/asset/%s/annotations/%s/">Selection</a>'
                '</p><p><a href="/asset/%s/annotations/%s/">Selection</a>'
                '</p><p><a href="/asset/%s/annotations/%s/">Alt Selection</a>'
                '</p><a href="/asset/%s/">Global</a></p>' %
                (old_asset.id, old_note.id,
                 old_asset.id, old_note.id,
                 old_asset.id, alt_note.id,
                 old_asset.id))

        new_text = new_note.update_references_in_string(text, old_note)

        citations = SherdNote.objects.references_in_string(new_text,
                                                           old_note.author)
        self.assertEqual(len(citations), 4)
        self.assertEqual(citations[0].id, new_note.id)
        self.assertEqual(citations[0].asset.id, new_note.asset.id)

        self.assertEqual(citations[1].id, new_note.id)
        self.assertEqual(citations[1].asset.id, new_note.asset.id)

        self.assertEqual(citations[2].id, alt_note.id)
        self.assertEqual(citations[2].asset.id, old_asset.id)

        gann = old_asset.global_annotation(self.student_one, auto_create=False)
        self.assertEqual(citations[3].id, gann.id)
        self.assertEqual(citations[3].asset.id, old_asset.id)

    def test_filter_by_vocabulary(self):
        taxonomy = {
            'Shapes': ['Square', 'Triangle'],
            'Colors': ['Red', 'Blue', 'Green']
        }
        self.create_vocabularies(self.sample_course, taxonomy)

        a1 = AssetFactory(course=self.sample_course, author=self.student_one)
        note1 = SherdNoteFactory(
            asset=a1, author=self.student_one,
            title="The Award", tags=',student_one_selection',
            body='student one selection note', range1=0, range2=1)
        note2 = SherdNoteFactory(
            asset=a1, author=self.student_two,
            title="Nice Tie", tags=',student_two_selection',
            body='student two selection note', range1=0, range2=1)
        note3 = SherdNoteFactory(
            asset=a1, author=self.instructor_one,
            title="Our esteemed leaders",
            tags=',image, instructor_one_selection,',
            body='instructor one selection note', range1=0, range2=1)

        # OR'd within vocabulary, AND'd across vocabulary
        shapes = Vocabulary.objects.get(name='shapes')
        colors = Vocabulary.objects.get(name='colors')

        red = Term.objects.get(name='red')
        blue = Term.objects.get(name='blue')
        green = Term.objects.get(name='green')
        square = Term.objects.get(name='square')
        triangle = Term.objects.get(name='triangle')

        self.create_term_relationship(note1, red)
        self.create_term_relationship(note2, blue)

        self.create_term_relationship(note3, red)
        self.create_term_relationship(note3, square)

        # get all notes that are tagged red or blue
        ctx = {'%s' % colors.id: [red.id]}
        notes = SherdNote.objects.filter_by_vocabulary(ctx)
        self.assertEqual(notes.count(), 2)

        ctx = {'%s' % colors.id: [blue.id]}
        notes = SherdNote.objects.filter_by_vocabulary(ctx)
        self.assertEqual(notes.count(), 1)

        ctx = {'%s' % colors.id: [red.id, blue.id]}
        notes = SherdNote.objects.filter_by_vocabulary(ctx)
        self.assertEqual(notes.count(), 3)

        ctx = {'%s' % shapes.id: [square.id]}
        notes = SherdNote.objects.filter_by_vocabulary(ctx)
        self.assertEqual(notes.count(), 1)

        ctx = {
            '%s' % colors.id: [blue.id],
            '%s' % shapes.id: [square.id]
        }
        notes = SherdNote.objects.filter_by_vocabulary(ctx)
        self.assertEqual(notes.count(), 0)

        ctx = {
            '%s' % colors.id: [red.id],
            '%s' % shapes.id: [square.id]
        }
        notes = SherdNote.objects.filter_by_vocabulary(ctx)
        self.assertEqual(notes.count(), 1)
        self.assertEqual(notes[0].title, "Our esteemed leaders")

        ctx = {
            '%s' % shapes.id: [triangle.id]
        }
        notes = SherdNote.objects.filter_by_vocabulary(ctx)
        self.assertEqual(notes.count(), 0)

        ctx = {
            '%s' % colors.id: [green.id],
            '%s' % shapes.id: [triangle.id]
        }
        notes = SherdNote.objects.filter_by_vocabulary(ctx)
        self.assertEqual(notes.count(), 0)

    def test_filter_by_today(self):
        note = SherdNoteFactory()

        # today
        notes = SherdNote.objects.filter_by_date('today')
        self.assertEqual(notes.count(), 1)
        self.assertEqual(notes[0].title, note.title)

        # yesterday
        notes = SherdNote.objects.filter_by_date('yesterday')
        self.assertEqual(notes.count(), 0)

        # in the last week
        notes = SherdNote.objects.filter_by_date('lastweek')
        self.assertEqual(notes.count(), 1)
        self.assertEqual(notes[0].title, note.title)


class SherdNoteFilterTest(MediathreadTestMixin, TestCase):

    def setUp(self):
        self.setup_sample_course()

        self.asset = AssetFactory(course=self.sample_course,
                                  author=self.student_one,
                                  primary_source='image',)

        self.student_one_ga = SherdNoteFactory(
            asset=self.asset, author=self.student_one,
            tags=',student_one_item', title=None, is_global_annotation=True)
        self.assertTrue(self.student_one_ga.is_global_annotation)
        self.student_one_note = SherdNoteFactory(
            asset=self.asset, author=self.student_one,
            tags=',student_one_selection', range1=0, range2=1)

        self.student_two_ga = SherdNoteFactory(
            asset=self.asset, author=self.student_two,
            tags=',student_two_item', title=None, is_global_annotation=True)
        self.student_two_note = SherdNoteFactory(
            asset=self.asset, author=self.student_two,
            tags=',student_two_selection', range1=0, range2=1)

        self.instructor_one_ga = SherdNoteFactory(
            asset=self.asset, author=self.instructor_one,
            tags=',instructor_one_item', title=None, is_global_annotation=True)
        self.instructor_one_note = SherdNoteFactory(
            asset=self.asset, author=self.instructor_one,
            tags=',image,instructor_one_selection,', range1=0, range2=1)

    def test_filter_by_record_owner(self):
        qs = Asset.objects.filter(id=self.asset.id)
        author = User.objects.get(username='student_one')

        names = ['instructor_one', 'instructor_two', 'student_one']
        users = User.objects.filter(username__in=names).values_list('id')
        visible_authors = users.values_list('id', flat=True)

        notes = SherdNote.objects.get_related_notes(qs,
                                                    author,
                                                    visible_authors,
                                                    True)
        self.assertEqual(notes.count(), 2)

        self.assertEqual(notes[0], self.student_one_ga)
        self.assertEqual(notes[1], self.student_one_note)

    def test_filter_no_authors(self):
        qs = Asset.objects.filter(id=self.asset.id)

        notes = SherdNote.objects.get_related_notes(qs, None, [], True)
        self.assertEqual(notes.count(), 6)

        self.assertEqual(notes[0], self.student_one_ga)
        self.assertEqual(notes[1], self.student_one_note)
        self.assertEqual(notes[2], self.student_two_ga)
        self.assertEqual(notes[3], self.student_two_note)
        self.assertEqual(notes[4], self.instructor_one_ga)
        self.assertEqual(notes[5], self.instructor_one_note)

    def test_filter_by_visible_authors(self):
        qs = Asset.objects.filter(id=self.asset.id)

        names = ['instructor_one', 'instructor_two', 'student_one']
        users = User.objects.filter(username__in=names).values_list('id')
        visible_authors = users.values_list('id', flat=True)

        notes = SherdNote.objects.get_related_notes(qs,
                                                    None,
                                                    visible_authors,
                                                    True)
        self.assertEqual(notes.count(), 5)

        self.assertEqual(notes[0], self.student_one_ga)
        self.assertEqual(notes[1], self.student_one_note)
        self.assertEqual(notes[2], self.student_two_ga)
        self.assertEqual(notes[3], self.instructor_one_ga)
        self.assertEqual(notes[4], self.instructor_one_note)

    def test_filter_by_all_items_are_visible(self):
        qs = Asset.objects.filter(id=self.asset.id)

        names = ['instructor_one', 'instructor_two', 'student_one']
        users = User.objects.filter(username__in=names).values_list('id')
        visible_authors = users.values_list('id', flat=True)

        notes = SherdNote.objects.get_related_notes(qs,
                                                    None,
                                                    visible_authors,
                                                    False)
        self.assertEqual(notes.count(), 4)

        self.assertEqual(notes[0], self.student_one_ga)
        self.assertEqual(notes[1], self.student_one_note)
        self.assertEqual(notes[2], self.instructor_one_ga)
        self.assertEqual(notes[3], self.instructor_one_note)

    def test_filter_by_tags(self):
        notes = SherdNote.objects.filter_by_tags('student_one_selection')
        self.assertEqual(notes.count(), 1)
        self.assertEqual(notes[0], self.student_one_note)

        notes = SherdNote.objects.filter(asset=self.asset)
        self.assertEqual(notes.count(), 6)

        notes = notes.filter_by_tags(
            'student_two_selection,image').order_by('id')
        self.assertEqual(notes.count(), 2)
        self.assertEqual(notes[0], self.student_two_note)
        self.assertEqual(notes[1], self.instructor_one_note)

    def test_get_related_assets(self):
        asset2 = AssetFactory(course=self.sample_course,
                              author=self.student_one)
        note2 = SherdNoteFactory(asset=asset2, author=self.student_one)

        ids = [self.student_one_ga.id, self.student_one_note.id, note2.id]
        notes = SherdNote.objects.filter(id__in=ids)

        assets = notes.get_related_assets()
        self.assertEqual(assets.count(), 2)
        self.assertTrue(self.asset in assets)
        self.assertTrue(asset2 in assets)

    def test_exclude_primary_types(self):
        asset2 = AssetFactory(course=self.sample_course,
                              author=self.student_one,
                              primary_source='youtube',)

        youtube_note = SherdNoteFactory(
            asset=asset2, author=self.student_one,
            tags=',student_one_selection', range1=0, range2=1)

        qs = SherdNote.objects.filter(author=self.student_one)
        self.assertEqual(qs.count(), 3)

        notes = qs.exclude_primary_types(['youtube'])
        self.assertEqual(notes.count(), 2)
        self.assertTrue(self.student_one_ga in notes)
        self.assertTrue(self.student_one_note in notes)

        notes = qs.exclude_primary_types(['image'])
        self.assertEqual(notes.count(), 1)
        self.assertEqual(notes[0], youtube_note)


class DiscussionIndexTest(MediathreadTestMixin, TestCase):

    def setUp(self):
        self.setup_sample_course()

        self.project = ProjectFactory.create(
            course=self.sample_course, author=self.student_one,
            policy='CourseProtected')
        self.collaboration = self.project.get_collaboration()

        self.asset = AssetFactory.create(course=self.sample_course,
                                         primary_source='image')
        self.asset2 = AssetFactory.create(course=self.sample_course,
                                          primary_source='image')

        self.note = SherdNoteFactory(
            asset=self.asset, author=self.student_one,
            tags=',student_one_selection',
            body='student one selection note', range1=0, range2=1)

        self.note2 = SherdNoteFactory(
            asset=self.asset2, author=self.student_one, title='note2')

    def update_references(self):
        DiscussionIndex.update_class_references(self.project.body,
                                                None, None,
                                                self.collaboration,
                                                self.project.author)

    def test_composition(self):
        self.add_citation(self.project, self.note)
        self.add_citation(self.project, self.note2)
        self.asset2.delete()

        self.update_references()

        indicies = DiscussionIndex.objects.all()
        self.assertEqual(indicies.count(), 1)
        index = indicies.first()
        self.assertIsNone(index.participant)
        self.assertIsNone(index.comment)
        self.assertEqual(index.collaboration, self.collaboration)
        self.assertEqual(index.asset, self.asset)

        self.assertEqual(index.get_type_label(), 'project')
        self.assertEqual(index.content_object, self.asset)
        self.assertEqual(index.clump_parent(), self.project)
        self.assertIsNone(index.get_parent_url())
        self.assertEqual(index.body, '')

    def test_selection_assignment(self):
        AssignmentItemFactory(project=self.project, asset=self.asset)

        self.update_references()

        indicies = DiscussionIndex.objects.all()
        self.assertEqual(indicies.count(), 1)

        index = indicies[0]
        self.assertIsNone(index.participant)
        self.assertIsNone(index.comment)
        self.assertEqual(index.collaboration, self.collaboration)
        self.assertEqual(index.asset, self.asset)

        self.assertEqual(index.get_type_label(), 'project')
        self.assertEqual(index.content_object, self.asset)
        self.assertEqual(index.clump_parent(), self.project)
        self.assertIsNone(index.get_parent_url())
        self.assertEqual(index.body, '')

    def test_selection_assignment_response(self):
        ProjectNoteFactory(project=self.project, annotation=self.note2)

        self.update_references()

        indicies = DiscussionIndex.objects.all()
        self.assertEqual(indicies.count(), 1)

        index = indicies[0]
        self.assertIsNone(index.participant)
        self.assertIsNone(index.comment)
        self.assertEqual(index.collaboration, self.collaboration)
        self.assertEqual(index.asset, self.asset2)

        self.assertEqual(index.get_type_label(), 'project')
        self.assertEqual(index.content_object, self.asset2)
        self.assertEqual(index.clump_parent(), self.project)
        self.assertIsNone(index.get_parent_url())
        self.assertEqual(index.body, '')

    def test_sequence(self):
        sa = SequenceAssetFactory(spine=self.note)
        ProjectSequenceAssetFactory(project=self.project, sequence_asset=sa)
        SequenceMediaElementFactory(sequence_asset=sa, media=self.note2)

        self.update_references()

        indicies = DiscussionIndex.objects.all()
        self.assertEqual(indicies.count(), 2)

        index = indicies[0]
        self.assertIsNone(index.participant)
        self.assertIsNone(index.comment)
        self.assertEqual(index.collaboration, self.collaboration)
        self.assertEqual(index.asset, self.asset)

        self.assertEqual(index.get_type_label(), 'project')
        self.assertEqual(index.content_object, self.asset)
        self.assertEqual(index.clump_parent(), self.project)
        self.assertIsNone(index.get_parent_url())
        self.assertEqual(index.body, '')

        index = indicies[1]
        self.assertIsNone(index.participant)
        self.assertIsNone(index.comment)
        self.assertEqual(index.collaboration, self.collaboration)
        self.assertEqual(index.asset, self.asset2)

        self.assertEqual(index.get_type_label(), 'project')
        self.assertEqual(index.content_object, self.asset2)
        self.assertEqual(index.clump_parent(), self.project)
        self.assertIsNone(index.get_parent_url())
        self.assertEqual(index.body, '')

    def test_discussion_references(self):
        self.create_discussion(self.sample_course, self.instructor_one)

        indicies = DiscussionIndex.objects.all()
        self.assertEqual(indicies.count(), 1)

        index = indicies.first()
        comment = ThreadedComment.objects.first()

        self.assertEqual(index.participant, comment.user)
        self.assertEqual(index.comment, comment.comment_ptr)
        self.assertEqual(index.collaboration, comment.content_object)
        self.assertIsNone(index.asset)

        self.assertEqual(index.get_type_label(), 'discussion')
        self.assertEqual(index.content_object, comment.content_object)
        self.assertEqual(index.clump_parent(group_by='discussion'),
                         comment.content_object)
        self.assertEqual(index.clump_parent(),
                         comment.content_object)
        self.assertEqual(index.get_parent_url(),
                         '/discussion/%s' % comment.id)
        self.assertEqual(index.body, '')
