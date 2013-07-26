from django.test import TestCase
from mediathread.assetmgr.models import Asset


class AssetViewTest(TestCase):
    # Use ``fixtures`` & ``urls`` as normal. See Django's ``TestCase``
    # documentation for the gory details.
    fixtures = ['unittest_sample_course.json']

    def test_detail_asset_json(self):
        asset = Asset.objects.get(id=1)
        self.assertTrue(asset is not None)

    def test_gallery_asset_json(self):
        asset = Asset.objects.get(id=1)
        self.assertTrue(asset is not None)
