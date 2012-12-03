from django.contrib.auth.models import User
from django.test import TestCase
from assetmgr.models import Asset
from djangosherd.models import SherdNote


class SherdNoteTest(TestCase):
    fixtures = ['unittest_sample_course.json']

    def test_is_global_annotation(self):
        # Alternate Course, test_student_three
        global_annotation = SherdNote.objects.get(id=16)
        self.assertTrue(global_annotation.is_global_annotation())
        self.assertTrue(global_annotation.title == None)
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
        
        a, created = SherdNote.objects.global_annotation(asset, author)
        self.assertFalse(created)
        self.assertEquals(a.title, None)
        self.assertEquals(a.body, "All credit to Mark and Casey")
        self.assertEquals(a.tags, ",youtube, test_instructor_item")
        
        author = User.objects.get(username="test_student_one")
        a, created = SherdNote.objects.global_annotation(asset, author)
        self.assertTrue(created)
        self.assertEquals(a.title, None)
        self.assertEquals(a.body, None)
        self.assertEquals(a.tags, '')
        
    def test_tags_split(self):        
        asset = Asset.objects.get(id=1)
        author = User.objects.get(username="test_instructor")
        
        a, created = SherdNote.objects.global_annotation(asset, author)
        tags = a.tags_split()
        self.assertEquals(len(tags), 2)        
        self.assertEquals(tags[0].name, 'test_instructor_item')
        self.assertEquals(tags[1].name, 'youtube')
        
        # Alternate course, student 3
        a = SherdNote.objects.get(id=15)
        tags = a.tags_split()
        self.assertEquals(len(tags), 1)
        self.assertEquals(tags[0].name, 'test_student_three')
        
        # Sample course, student on3
        author = User.objects.get(username="test_student_one")
        a, created = SherdNote.objects.global_annotation(asset, author)
        self.assertTrue(created)
        tags = a.tags_split()
        self.assertEquals(len(tags), 0)

    def test_add_tag(self):
        a = SherdNote.objects.get(id=15)
        a.add_tag("foo")
        a.add_tag("bar")
        a.save()
        
        tags = a.tags_split()
        self.assertEquals(len(tags), 3)
        self.assertEquals(tags[0].name, 'bar')
        self.assertEquals(tags[1].name, 'foo')
        self.assertEquals(tags[2].name, 'test_student_three')
        
