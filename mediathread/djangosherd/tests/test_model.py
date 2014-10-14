# pylint: disable-msg=R0904
from django.contrib.auth.models import User
from django.test import TestCase

from mediathread.assetmgr.models import Asset
from mediathread.djangosherd.models import SherdNote
from mediathread.factories import AssetFactory, \
    SherdNoteFactory, MediathreadTestMixin
from mediathread.taxonomy.models import Vocabulary, Term


class SherdNoteTest(MediathreadTestMixin, TestCase):

    def setUp(self):
        self.setup_sample_course()

    def test_is_global_annotation(self):
        asset = AssetFactory(course=self.sample_course)
        global_annotation, created = SherdNote.objects.global_annotation(
            asset, self.student_three, auto_create=True)
        self.assertTrue(global_annotation.is_global_annotation())

        whole_item_annotation = SherdNoteFactory(
            asset=asset, author=self.student_three,
            title="Whole Item Selection", range1=0, range2=0)
        self.assertFalse(whole_item_annotation.is_global_annotation())

        real_annotation = SherdNoteFactory(
            asset=asset, author=self.student_three,
            title="Whole Item Selection", range1=116.25, range2=6.75)
        self.assertFalse(real_annotation.is_global_annotation())

    def test_seconds_to_code(self):
        self.assertRaises(TypeError, SherdNote.secondsToCode, None)
        self.assertEquals(SherdNote.secondsToCode(0), "0:00")
        self.assertEquals(SherdNote.secondsToCode(5), "0:05")
        self.assertEquals(SherdNote.secondsToCode(60), "01:00")
        self.assertEquals(SherdNote.secondsToCode(120), "02:00")
        self.assertEquals(SherdNote.secondsToCode(3600, True), "01:00:00")
        self.assertEquals(SherdNote.secondsToCode(6400), "01:46:40")
        self.assertEquals(SherdNote.secondsToCode(86400, True), "24:00:00")
        self.assertEquals(SherdNote.secondsToCode(363600, True), "101:00:00")

    def test_range_as_timecode(self):
        asset = AssetFactory(course=self.sample_course)

        global_annotation, created = SherdNote.objects.global_annotation(
            asset, self.student_three, auto_create=True)
        self.assertEquals(global_annotation.range_as_timecode(), "")

        whole_item_annotation = SherdNoteFactory(
            asset=asset, author=self.student_three)
        self.assertEquals(whole_item_annotation.range_as_timecode(), "")

        real_annotation = SherdNoteFactory(
            asset=asset, author=self.student_three, range1=28, range2=39)
        self.assertEquals(real_annotation.range_as_timecode(), "0:28 - 0:39")

        real_annotation = SherdNoteFactory(
            asset=asset, author=self.student_three, range1=43, range2=75)
        self.assertEquals(real_annotation.range_as_timecode(), "0:43 - 01:15")

    def test_get_global_annotation(self):
        asset = AssetFactory(course=self.sample_course)
        author = self.instructor_one

        ann, created = SherdNote.objects.global_annotation(asset, author)
        self.assertTrue(created)

        ann, created = SherdNote.objects.global_annotation(asset, author)
        self.assertFalse(created)

        self.assertEquals(ann.title, None)
        self.assertEquals(ann.title, None)
        self.assertEquals(ann.body, None)
        self.assertEquals(ann.tags, '')

        author = self.student_one
        ann, created = SherdNote.objects.global_annotation(asset, author)
        self.assertTrue(created)
        self.assertEquals(ann.title, None)
        self.assertEquals(ann.body, None)
        self.assertEquals(ann.tags, '')

    def test_tags_split(self):
        asset = AssetFactory(course=self.sample_course)
        ann, created = SherdNote.objects.global_annotation(
            asset, self.instructor_one)

        # no tags
        tags = ann.tags_split()
        self.assertEquals(len(tags), 0)

        # one tag
        ann.tags = ',foobar'
        ann.save()
        tags = ann.tags_split()
        self.assertEquals(len(tags), 1)
        self.assertEquals(tags[0].name, 'foobar')

        # two tags
        ann.tags = ',youtube, test_instructor_item'
        ann.save()
        tags = ann.tags_split()
        self.assertEquals(len(tags), 2)
        self.assertEquals(tags[0].name, 'test_instructor_item')
        self.assertEquals(tags[1].name, 'youtube')

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
        self.assertEquals(len(tags), 3)
        self.assertEquals(tags[0].name, 'bar')
        self.assertEquals(tags[1].name, 'foo')
        self.assertEquals(tags[2].name, 'foobar')

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
        self.assertEquals(len(citations), 4)
        self.assertEquals(citations[0].id, new_note.id)
        self.assertEquals(citations[0].asset.id, new_note.asset.id)

        self.assertEquals(citations[1].id, new_note.id)
        self.assertEquals(citations[1].asset.id, new_note.asset.id)

        self.assertEquals(citations[2].id, alt_note.id)
        self.assertEquals(citations[2].asset.id, old_asset.id)

        gann = old_asset.global_annotation(self.student_one, auto_create=False)
        self.assertEquals(citations[3].id, gann.id)
        self.assertEquals(citations[3].asset.id, old_asset.id)

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
        self.assertEquals(notes.count(), 2)

        ctx = {'%s' % colors.id: [blue.id]}
        notes = SherdNote.objects.filter_by_vocabulary(ctx)
        self.assertEquals(notes.count(), 1)

        ctx = {'%s' % colors.id: [red.id, blue.id]}
        notes = SherdNote.objects.filter_by_vocabulary(ctx)
        self.assertEquals(notes.count(), 3)

        ctx = {'%s' % shapes.id: [square.id]}
        notes = SherdNote.objects.filter_by_vocabulary(ctx)
        self.assertEquals(notes.count(), 1)

        ctx = {
            '%s' % colors.id: [blue.id],
            '%s' % shapes.id: [square.id]
        }
        notes = SherdNote.objects.filter_by_vocabulary(ctx)
        self.assertEquals(notes.count(), 0)

        ctx = {
            '%s' % colors.id: [red.id],
            '%s' % shapes.id: [square.id]
        }
        notes = SherdNote.objects.filter_by_vocabulary(ctx)
        self.assertEquals(notes.count(), 1)
        self.assertEquals(notes[0].title, "Our esteemed leaders")

        ctx = {
            '%s' % shapes.id: [triangle.id]
        }
        notes = SherdNote.objects.filter_by_vocabulary(ctx)
        self.assertEquals(notes.count(), 0)

        ctx = {
            '%s' % colors.id: [green.id],
            '%s' % shapes.id: [triangle.id]
        }
        notes = SherdNote.objects.filter_by_vocabulary(ctx)
        self.assertEquals(notes.count(), 0)

    def test_filter_by_today(self):
        note = SherdNoteFactory()

        # today
        notes = SherdNote.objects.filter_by_date('today')
        self.assertEquals(notes.count(), 1)
        self.assertEquals(notes[0].title, note.title)

        # yesterday
        notes = SherdNote.objects.filter_by_date('yesterday')
        self.assertEquals(notes.count(), 0)

        # in the last week
        notes = SherdNote.objects.filter_by_date('lastweek')
        self.assertEquals(notes.count(), 1)
        self.assertEquals(notes[0].title, note.title)


class SherdNoteFilterTest(MediathreadTestMixin, TestCase):

    def setUp(self):
        self.setup_sample_course()

        self.asset = AssetFactory(course=self.sample_course,
                                  author=self.student_one)

        self.ga1 = SherdNoteFactory(
            asset=self.asset, author=self.student_one,
            tags=',student_one_item', title=None, range1=None, range2=None)
        self.assertTrue(self.ga1.is_global_annotation())
        self.note1 = SherdNoteFactory(
            asset=self.asset, author=self.student_one,
            tags=',student_one_selection', range1=0, range2=1)

        self.ga2 = SherdNoteFactory(
            asset=self.asset, author=self.student_two,
            tags=',student_two_item', title=None, range1=None, range2=None)
        self.note2 = SherdNoteFactory(
            asset=self.asset, author=self.student_two,
            tags=',student_two_selection', range1=0, range2=1)

        self.ga3 = SherdNoteFactory(
            asset=self.asset, author=self.instructor_one,
            tags=',instructor_one_item', title=None, range1=None, range2=None)
        self.note3 = SherdNoteFactory(
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
                                                    visible_authors)
        self.assertEquals(notes.count(), 2)

        self.assertEquals(notes[0], self.ga1)
        self.assertEquals(notes[1], self.note1)

    def test_filter_no_authors(self):
        qs = Asset.objects.filter(id=self.asset.id)

        notes = SherdNote.objects.get_related_notes(qs, None, [])
        self.assertEquals(notes.count(), 6)

        self.assertEquals(notes[0], self.ga1)
        self.assertEquals(notes[1], self.note1)
        self.assertEquals(notes[2], self.ga2)
        self.assertEquals(notes[3], self.note2)
        self.assertEquals(notes[4], self.ga3)
        self.assertEquals(notes[5], self.note3)

    def test_filter_by_visible_authors(self):
        qs = Asset.objects.filter(id=self.asset.id)

        names = ['instructor_one', 'instructor_two', 'student_one']
        users = User.objects.filter(username__in=names).values_list('id')
        visible_authors = users.values_list('id', flat=True)

        notes = SherdNote.objects.get_related_notes(qs,
                                                    None,
                                                    visible_authors)
        self.assertEquals(notes.count(), 4)

        self.assertEquals(notes[0], self.ga1)
        self.assertEquals(notes[1], self.note1)
        self.assertEquals(notes[2], self.ga3)
        self.assertEquals(notes[3], self.note3)

    def test_filter_by_tags(self):
        notes = SherdNote.objects.filter_by_tags('student_one_selection')
        self.assertEquals(notes.count(), 1)
        self.assertEquals(notes[0], self.note1)

        notes = SherdNote.objects.filter(asset=self.asset)
        self.assertEquals(notes.count(), 6)

        notes = notes.filter_by_tags(
            'student_two_selection,image').order_by('id')
        self.assertEquals(notes.count(), 2)
        self.assertEquals(notes[0], self.note2)
        self.assertEquals(notes[1], self.note3)
