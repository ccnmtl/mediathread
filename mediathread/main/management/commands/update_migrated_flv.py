from django.core.management.base import BaseCommand

from mediathread.assetmgr.models import Source


class Command(BaseCommand):

    help = 'Migrate flvs with an mp4 match'

    def add_arguments(self, parser):
        parser.add_argument('-f', '--fake', action='store_true')

    def handle(self, *app_labels, **options):

        # For each flv in the system, see if there is an mp4_pseudo match
        # Match occurs very simply by title. There is a risk of overlap
        # but a quick review of videos reveals this to be okay
        uploaded = 'Mediathread video uploaded by'
        sources = Source.objects.filter(
            primary=True, label__in=['flv_pseudo', 'flv']).exclude(
                asset__title__isnull=True).exclude(
                asset__title__exact='').exclude(
                asset__title__startswith=uploaded).select_related('asset')

        n = 1
        for source in sources:
            mp4_source = Source.objects.filter(
                primary=True, label='mp4_pseudo',
                asset__title=source.asset.title).exclude(
                url__isnull=True).exclude(url__exact='').first()

            if mp4_source:
                msg = '{}, {}, {}, {}, {}, {}, {}'.format(
                    source.asset.title,
                    source.asset.course.title.encode('utf-8').strip(),
                    source.asset.id,
                    mp4_source.asset.course.title.encode('utf-8').strip(),
                    mp4_source.asset.id,
                    source.url, mp4_source.url)
                print msg

                if not options['fake']:
                    source.asset.update_primary('mp4_pseudo', mp4_source.url)
                n += 1

        print 'Updated {}'.format(n)
