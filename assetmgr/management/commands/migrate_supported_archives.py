from django.core.management.base import BaseCommand, CommandError
from mediathread.assetmgr.supported_archives import all
from mediathread.assetmgr.models import SupportedSource

class Command(BaseCommand):

    def handle(self, *app_labels, **options):
        for a in all:
            SupportedSource.objects.create(title=a['title'],
                                           archive_url = a['sources']['archive']['url'],
                                           thumb_url = a['sources']['thumb']['url'],
                                           description = a['metadata']['description'])
            