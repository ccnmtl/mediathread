from assetmgr.models import Asset
from courseaffils.models import Course
from django.contrib.auth.models import User
from django.test import TestCase
from djangosherd.models import SherdNote


class AssetTest(TestCase):
    fixtures = ['unittest_sample_course.json']

    def test_video(self):
        # youtube -- asset #1
        asset = Asset.objects.get(id=1)
        self.assertEquals(asset.media_type(), 'video')
        self.assertFalse(asset.primary.is_image())
        self.assertFalse(asset.primary.is_archive())
        self.assertFalse(asset.primary.is_audio())

    def test_image(self):
        # image -- asset #2
        asset = Asset.objects.get(id=2)

        self.assertEquals(asset.media_type(), 'image')
        self.assertTrue(asset.primary.is_image())
        self.assertFalse(asset.primary.is_archive())
        self.assertFalse(asset.primary.is_audio())

    def test_migrate_many(self):
        self.assertTrue(True)

    def test_migrate_one(self):
        asset = Asset.objects.get(id=1)
        self.assertEquals(asset.title, "Mediathread: Introduction")

        new_course = Course.objects.get(id=2)
        self.assertEquals(new_course.title, "Alternate Course")

        new_user = User.objects.get(username='test_instructor_alt')

        new_asset = Asset.objects.migrate_one(asset, new_course, new_user)
        self.assertEquals(new_asset.author, new_user)
        self.assertEquals(new_asset.course, new_course)

        self.assertEquals(new_asset.media_type(), 'video')
        self.assertFalse(new_asset.primary.is_image())
        self.assertFalse(new_asset.primary.is_archive())
        self.assertFalse(new_asset.primary.is_audio())

        # migrate annotations as well
        # global_annotation = SherdNote.objects.get(id=1)
        # new_note = SherdNote.objects.migrate_one(global_annotation,
        #                                         new_asset,
        #                                         new_user)
        # self.assertTrue(new_note.is_global_annotation())
        # self.assertEquals(global_annotation.title, None)
        # self.assertEquals(new_note.body, "student three item note")

    def test_update_reference_in_string(self):
        text = ('<p><a href="/asset/2/annotations/10/">Nice Tie</a>'
                '</p><p><a href="/asset/2/annotations/10/">Nice Tie</a>'
                '</p><p><a href="/asset/2/annotations/8/">Nice Tie</a>'
                '</p><a href="/asset/2/">Whole Item</a></p>')

        old_asset = Asset.objects.get(id=2)
        new_asset = Asset.objects.get(id=1)

        new_text = new_asset.update_references_in_string(text, old_asset)

        citations = SherdNote.objects.references_in_string(new_text,
                                                           new_asset.author)
        self.assertEquals(len(citations), 4)
        self.assertEquals(citations[0].id, 10)
        self.assertEquals(citations[0].asset.id, 2)

        self.assertEquals(citations[1].id, 10)
        self.assertEquals(citations[1].asset.id, 2)

        self.assertEquals(citations[2].id, 8)
        self.assertEquals(citations[2].asset.id, 2)

        self.assertEquals(citations[3].id, 1)
        self.assertEquals(citations[3].asset.id, 1)
