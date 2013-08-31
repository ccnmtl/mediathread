#pylint: disable-msg=R0904
from mediathread.assetmgr.models import Asset
from django.contrib.auth.models import User
from django.test import TestCase
from mediathread.djangosherd.models import SherdNote


class SherdNoteTest(TestCase):
    fixtures = ['unittest_sample_course.json']

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
