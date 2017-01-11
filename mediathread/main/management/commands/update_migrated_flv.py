from django.core.management.base import BaseCommand

from mediathread.assetmgr.models import Source


class Command(BaseCommand):

    def handle(self, *app_labels, **options):
        # For each flv in the system, see if there is an mp4_pseudo match
        # Match occurs very simply by title
        sources = Source.objects.filter(
            primary=True, label__in=['flv_pseudo', 'flv']).exclude(
                asset__title__isnull=True).exclude(asset__title__exact='')
        print 'Found {} sources'.format(sources.count())

        n = 1
        for source in sources:
            mp4_source = Source.objects.filter(
                primary=True, label='mp4_pseudo',
                asset__title=source.asset.title).exclude(
                url__isnull=True).exclude(url__exact='').first()

            if mp4_source:
                print '{}, {}, {}, {}, {}'.format(
                    source.asset.title, source.asset.id, mp4_source.asset.id,
                    source.url, mp4_source.url)
                n += 1
                #source.asset.update_primary('mp4_pseudo', mp4_source.url)

        print 'Updated {}'.format(n)