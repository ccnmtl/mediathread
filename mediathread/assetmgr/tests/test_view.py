from django.contrib.auth.models import User
from django.test import TestCase
from django.test.client import RequestFactory
from mediathread.assetmgr.api import AssetResource
from mediathread.assetmgr.models import Asset


class AssetViewTest(TestCase):
    # Use ``fixtures`` & ``urls`` as normal. See Django's ``TestCase``
    # documentation for the gory details.
    fixtures = ['unittest_sample_course.json']

    def setUp(self):
        # Every test needs access to the request factory.
        self.factory = RequestFactory()

    def test_asset_resource(self):
        request = self.factory.get("/asset/1/")
        request.user = User.objects.get(id=1)

        asset = Asset.objects.get(id=1)
        resource = AssetResource()
        resource.render_one(request, asset)
