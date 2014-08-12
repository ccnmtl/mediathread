#pylint: disable-msg=R0904
from courseaffils.models import Course
from datetime import datetime
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from mediathread.assetmgr.models import Asset
from mediathread.djangosherd.models import SherdNote
from mediathread.taxonomy.models import Vocabulary, Term, TermRelationship


class SherdNoteTest(TestCase):
    fixtures = ['unittest_sample_course.json']

    def create_vocabularies(self, course, taxonomy):
        course_type = ContentType.objects.get_for_model(course)

        for name, terms in taxonomy.items():
            concept = Vocabulary(display_name=name,
                                 content_type=course_type,
                                 object_id=course.id)
            concept.save()
            for term_name in terms:
                term = Term(display_name=term_name,
                            vocabulary=concept)
                term.save()

    def create_term_relationship(self, content_object, term):
        # Add some tags to a few notes
        content_type = ContentType.objects.get_for_model(content_object)
        TermRelationship.objects.get_or_create(
            term=term,
            content_type=content_type,
            object_id=content_object.id)

    def setUp(self):
        course = Course.objects.get(title="Sample Course")
        taxonomy = {
            'Shapes': ['Square', 'Triangle'],
            'Colors': ['Red', 'Blue', 'Green']
        }
        self.create_vocabularies(course, taxonomy)

    def test_is_global_annotation(self):
        # Alternate Course, test_student_three
        global_annotation = SherdNote.objects.get(id=16)
        self.assertTrue(global_annotation.is_global_annotation())
        self.assertEquals(global_annotation.title, None)
        self.assertEquals(global_annotation.body, "student three item note")

        # Alternate Course, test_student_three
        whole_item_annotation = SherdNote.objects.get(id=15)
        self.assertFalse(whole_item_annotation.is_global_annotation())
        self.assertEquals(whole_item_annotation.title, "Whole Item Selection")
        self.assertEquals(whole_item_annotation.range1, 0.0)
        self.assertEquals(whole_item_annotation.range2, 0.0)

        # Alternate Course, test_instructor_alt
        real_annotation = SherdNote.objects.get(id=14)
        self.assertFalse(real_annotation.is_global_annotation())
        self.assertEquals(real_annotation.title, "Curricular Context")
        self.assertEquals(real_annotation.range1, 116.25)
        self.assertEquals(real_annotation.range2, 6.75)

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
        # Sample Course Test Instructor
        global_annotation = SherdNote.objects.get(id=1)
        self.assertEquals(global_annotation.range_as_timecode(), "")

        whole_item_annotation = SherdNote.objects.get(id=17)
        self.assertEquals(whole_item_annotation.range_as_timecode(), "")

        real_annotation = SherdNote.objects.get(id=2)
        self.assertEquals(real_annotation.range_as_timecode(), "0:28 - 0:39")

        real_annotation = SherdNote.objects.get(id=3)
        self.assertEquals(real_annotation.range_as_timecode(), "0:43 - 01:15")

    def test_get_global_annotation(self):
        asset = Asset.objects.get(id=1)
        author = User.objects.get(username="test_instructor")

        ann, created = SherdNote.objects.global_annotation(asset, author)
        self.assertFalse(created)
        self.assertEquals(ann.title, None)
        self.assertEquals(ann.body, "All credit to Mark and Casey")
        self.assertEquals(ann.tags, ",youtube, test_instructor_item")

        author = User.objects.get(username="test_student_one")
        ann, created = SherdNote.objects.global_annotation(asset, author)
        self.assertTrue(created)
        self.assertEquals(ann.title, None)
        self.assertEquals(ann.body, None)
        self.assertEquals(ann.tags, '')

    def test_tags_split(self):
        asset = Asset.objects.get(id=1)
        author = User.objects.get(username="test_instructor")

        ann, created = SherdNote.objects.global_annotation(asset, author)
        tags = ann.tags_split()
        self.assertEquals(len(tags), 2)
        self.assertEquals(tags[0].name, 'test_instructor_item')
        self.assertEquals(tags[1].name, 'youtube')

        # Alternate course, student 3
        ann = SherdNote.objects.get(id=15)
        tags = ann.tags_split()
        self.assertEquals(len(tags), 1)
        self.assertEquals(tags[0].name, 'test_student_three')

        # Sample course, student on3
        author = User.objects.get(username="test_student_one")
        ann, created = SherdNote.objects.global_annotation(asset, author)
        self.assertTrue(created)
        tags = ann.tags_split()
        self.assertEquals(len(tags), 0)

    def test_add_tag(self):
        ann = SherdNote.objects.get(id=15)
        ann.add_tag("foo")
        ann.add_tag("bar")
        ann.save()

        tags = ann.tags_split()
        self.assertEquals(len(tags), 3)
        self.assertEquals(tags[0].name, 'bar')
        self.assertEquals(tags[1].name, 'foo')
        self.assertEquals(tags[2].name, 'test_student_three')

    def test_update_reference_in_string(self):
        text = ('<p><a href="/asset/2/annotations/10/">Nice Tie</a>'
                '</p><p><a href="/asset/2/annotations/10/">Nice Tie</a>'
                '</p><p><a href="/asset/2/annotations/8/">Nice Tie</a>'
                '</p><a href="/asset/2/">Whole Item</a></p>')

        old_note = SherdNote.objects.get(id=10)
        new_note = SherdNote.objects.get(id=2)

        new_text = new_note.update_references_in_string(text, old_note)

        citations = SherdNote.objects.references_in_string(new_text,
                                                           old_note.author)
        self.assertEquals(len(citations), 4)
        self.assertEquals(citations[0].id, new_note.id)
        self.assertEquals(citations[0].asset.id, new_note.asset.id)

        self.assertEquals(citations[1].id, new_note.id)
        self.assertEquals(citations[1].asset.id, new_note.asset.id)

        self.assertEquals(citations[2].id, 8)
        self.assertEquals(citations[2].asset.id, 2)

        self.assertEquals(citations[3].id, 11)
        self.assertEquals(citations[3].asset.id, 2)

    def test_update_reference_in_string2(self):
        text = ('<p><a href="/asset/1/annotations/1/">Foo</a>'
                '</p><p><a href="/asset/1/annotations/19/">Bar</a></p>')
        old_note = SherdNote.objects.get(id=1)
        new_note = SherdNote.objects.get(id=5)

        new_text = new_note.update_references_in_string(text, old_note)

        new_note_href = "/asset/%s/annotations/%s/" % (new_note.asset.id,
                                                       new_note.id)
        self.assertTrue(new_text.find(new_note_href) > 0)

        citations = SherdNote.objects.references_in_string(new_text,
                                                           old_note.author)
        self.assertEquals(len(citations), 2)

        self.assertEquals(citations[0].id, new_note.id)
        self.assertEquals(citations[0].asset.id, new_note.asset.id)

        self.assertEquals(citations[1].id, 19)
        self.assertEquals(citations[1].asset.id, 1)

    def test_filter_by_authors(self):
        qs = Asset.objects.filter(title='MAAP Award Reception')
        author = User.objects.get(username='test_student_one')

        names = ['test_instructor', 'test_instructor_two', 'test_student_one']
        users = User.objects.filter(username__in=names).values_list('id')
        visible_authors = users.values_list('id', flat=True)

        notes = SherdNote.objects.get_related_notes(qs,
                                                    author,
                                                    visible_authors)
        self.assertEquals(notes.count(), 3)

        self.assertEquals(notes[0].author.username, "test_instructor")
        self.assertFalse(notes[0].is_global_annotation())
        self.assertEquals(notes[0].title, 'Our esteemed leaders')

        self.assertEquals(notes[1].author, author)
        self.assertEquals(notes[1].title, "The Award")
        self.assertFalse(notes[1].is_global_annotation())

        self.assertEquals(notes[2].author, author)
        self.assertTrue(notes[2].is_global_annotation())

    def test_filter_by_date(self):
        notes = SherdNote.objects.filter_by_date('today')
        self.assertEquals(notes.count(), 0)

        notes = SherdNote.objects.filter_by_date('yesterday')
        self.assertEquals(notes.count(), 0)

        notes = SherdNote.objects.filter_by_date('lastweek')
        self.assertEquals(notes.count(), 0)

        today_note = SherdNote.objects.get(title='Nice Tie')
        today_note.modified = datetime.today()
        today_note.save()

        notes = SherdNote.objects.filter_by_date('today')
        self.assertEquals(notes.count(), 1)
        self.assertEquals(notes[0].title, 'Nice Tie')

    def test_filter_by_tags(self):
        notes = SherdNote.objects.filter_by_tags('student_one_selection')
        self.assertEquals(notes.count(), 1)
        self.assertEquals(notes[0].title, 'The Award')

        notes = SherdNote.objects.filter(asset__title='MAAP Award Reception')
        self.assertEquals(notes.count(), 6)

        notes = notes.filter_by_tags(
            'student_two_selection,image').order_by('id')
        self.assertEquals(notes.count(), 2)
        self.assertEquals(notes[0].title, 'Our esteemed leaders')
        self.assertEquals(notes[1].title, 'Nice Tie')

    def test_filter_by_vocabulary(self):
        # OR'd within vocabulary, AND'd across vocabulary
        shapes = Vocabulary.objects.get(name='shapes')
        colors = Vocabulary.objects.get(name='colors')

        red = Term.objects.get(name='red')
        blue = Term.objects.get(name='blue')
        green = Term.objects.get(name='green')
        square = Term.objects.get(name='square')
        triangle = Term.objects.get(name='triangle')

        note1 = SherdNote.objects.get(title='The Award')
        self.create_term_relationship(note1, red)
        note2 = SherdNote.objects.get(title='Nice Tie')
        self.create_term_relationship(note2, blue)

        note3 = SherdNote.objects.get(title='Our esteemed leaders')
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
