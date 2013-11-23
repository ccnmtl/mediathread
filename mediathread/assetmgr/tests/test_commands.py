#pylint: disable-msg=R0904
from courseaffils.models import Course
from django.contrib.auth.models import User
from django.core import management
from django.test import TestCase
from mediathread.assetmgr.models import Asset, Source


class AssetCommandsTest(TestCase):
    fixtures = ['unittest_sample_course.json']

    def test_migrate_artstor_assets(self):
        course = Course.objects.get(id=1)
        author = User.objects.get(username='test_instructor')

        asset = Asset(metadata_blob='{"artstor-id": ["SKIDMORE_10312643267"]}',
                      title="Test Asset",
                      active=True,
                      course=course,
                      author=author)
        asset.save()

        old_image_fpx = Source(asset=asset,
                               label='image_fpx',
                               url="the old image fpx url",
                               width=1024,
                               height=768,
                               primary=True,
                               media_type='fpx')
        old_image_fpx.save()
        self.assertTrue(old_image_fpx.primary)

        management.call_command("migrate_artstor_assets")

        s = Source.objects.filter(asset=asset, label='image_fpx')
        self.assertEquals(len(s), 0)

        s = Source.objects.get(asset=asset, label='deprecated_image_fpx')
        self.assertFalse(s.primary)

        s = Source.objects.get(asset=asset, label='image_fpxid')
        self.assertEquals(s.label, "image_fpxid")
        self.assertEquals(s.url, "SKIDMORE_10312643267")
        self.assertTrue(s.primary)
        self.assertEquals(s.width, 1024)
        self.assertEquals(s.height, 768)
