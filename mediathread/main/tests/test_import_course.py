#pylint: disable-msg=R0904
#pylint: disable-msg=E1103
# flake8: noqa
from courseaffils.models import Course
from django.contrib.auth.models import User
from django.test import TestCase
from django.test.client import Client
from mediathread.assetmgr.models import Asset
from mediathread.main.management.commands.import_course import Command
import os


class ImportCourseTest(TestCase):
    fixtures = ['unittest_sample_course.json']

    def test_import_course(self):
        client = Client()

        self.assertTrue(
            client.login(username='selenium', password='selenium'))

        test_instructor = User.objects.get(username="test_instructor")
        test_student_one = User.objects.get(username="test_student_one")
        test_student_two = User.objects.get(username="test_student_two")

        json_file = os.path.join(os.path.dirname(__file__),
                                 "test_import_course.json")

        course = Course.objects.get(title="Alternate Course")
        self.assertEquals(len(course.asset_set.all()), 1)

        cmd = Command()
        cmd.import_course_data(json_file, course)

        self.assertEquals(len(course.asset_set.all()), 2)

        asset = Asset.objects.get(title="GRFS_20130118_Patricia_Math_1_4")
        self.assertEquals(test_instructor, asset.author)
        self.assertEquals(asset.metadata_blob,
            u'{"wardenclyffe-id": ["10000"], "license": [""], "uuid": ["99dc990e-657f-11e2-a300-0017f20ea192"], "language": [""], "creator": ["jeh2199"], "tag": ["upload"], "subject": [""], "description": [""]}')

        self.assertEquals(2, len(asset.source_set.all()))
        source = asset.source_set.get(label="mp4_pseudo")
        self.assertEquals(source.url,
            u'http://stream.ccnmtl.columbia.edu/secvideos/SECURE/9a03f274-657f-11e2-a300-0017f20ea192-GRFS_20130118_Patricia_Lit_1_3-mp4-aac-480w-850kbps-ffmpeg.mp4')
        self.assertTrue(source.primary)
        self.assertEquals(source.width, 0)
        self.assertEquals(source.height, 0)
        self.assertEquals(source.media_type, None)

        source = asset.source_set.get(label="thumb")
        self.assertFalse(source.primary)
        self.assertEquals(source.url,
            u'http://wardenclyffe.ccnmtl.columbia.edu/uploads/images/10000/00000025.jpg')
        self.assertEquals(source.width, 0)
        self.assertEquals(source.height, 0)
        self.assertEquals(source.media_type, None)

        annotations = asset.sherdnote_set.all().order_by("id")
        self.assertEquals(14, len(annotations))

        ann = annotations[0]
        self.assertEquals(ann.author, test_instructor)
        self.assertTrue(ann.is_global_annotation())
        self.assertIsNone(ann.range1)
        self.assertIsNone(ann.range2)
        self.assertIsNone(ann.title)

        ann = annotations[1]
        self.assertEquals(ann.author, test_student_two)
        self.assertTrue(ann.is_global_annotation())
        self.assertIsNone(ann.range1)
        self.assertIsNone(ann.range2)
        self.assertIsNone(ann.title)

        ann = annotations[2]
        self.assertEquals(ann.author, test_student_one)
        self.assertTrue(ann.is_global_annotation())
        self.assertIsNone(ann.range1)
        self.assertIsNone(ann.range2)
        self.assertIsNone(ann.title)

        ann = annotations[3]
        self.assertEquals(ann.author, test_student_one)
        self.assertFalse(ann.is_global_annotation())
        self.assertEquals(ann.range1, 30.0)
        self.assertEquals(ann.range2, 30.0)
        self.assertEquals(ann.title, 'Part 1: Introduction ')
        self.assertEquals(ann.annotation_data,
            u'{"startCode":"00:00:30","endCode":"00:00:30","duration":0,"timeScale":1,"start":30,"end":30}')
        self.assertTrue(ann.body.startswith('CCNMTL- Still shot should be PDF of picture'))

        ann = annotations[9]
        self.assertEquals(ann.author, test_student_one)
        self.assertFalse(ann.is_global_annotation())
        self.assertEquals(ann.title, 'Part 5: Voiceover')
        self.assertFalse(ann.is_global_annotation())
        self.assertEquals(ann.range1, 123.0)
        self.assertEquals(ann.range2, 137.0)

        self.assertEquals(ann.annotation_data,
            u'{"startCode":"00:01:63","endCode":"00:02:17","duration":0,"timeScale":1,"start":123,"end":137}')
        self.assertTrue(ann.body.startswith, 'CCNMTL - please remove sound')
        self.assertEquals(ann.tags, ",moving voiceover")
