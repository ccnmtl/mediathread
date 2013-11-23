from django.core.management.base import BaseCommand
from mediathread.assetmgr.models import Asset, Source


class Command(BaseCommand):

    def handle(self, *app_labels, **options):
        assets = Asset.objects.filter(metadata_blob__contains='artstor-id')
        for asset in assets:
            fpx_id = asset.metadata()['artstor-id'][0]

            old_image_fpx = Source.objects.get(asset=asset,
                                               label='image_fpx')
            old_image_fpx.primary = False
            old_image_fpx.label = "deprecated_image_fpx"
            old_image_fpx.save()

            source = Source(asset=asset,
                            label='image_fpxid',
                            url=fpx_id,
                            height=old_image_fpx.height,
                            width=old_image_fpx.width,
                            primary=True,
                            media_type='fpx',
                            size=0)

            source.save()

            print "%s [%s]: added image_fpx source %s" % (asset.title,
                                                          asset.id,
                                                          fpx_id)
