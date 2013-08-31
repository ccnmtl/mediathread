from django.core.management.base import BaseCommand
from mediathread.assetmgr.supported_archives import all_archives
from mediathread.assetmgr.models import SupportedSource


class Command(BaseCommand):

    def handle(self, *app_labels, **options):
        for item in all_archives:
            SupportedSource.objects.create(
                title=item['title'],
                archive_url=item['sources']['archive']['url'],
                thumb_url=item['sources']['thumb']['url'],
                description=item['metadata']['description'])
