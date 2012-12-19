from django.test import TestCase
from assetmgr.models import Asset


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
