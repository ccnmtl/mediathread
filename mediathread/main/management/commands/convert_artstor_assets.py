from django.core.management.base import BaseCommand
from mediathread.assetmgr.models import Source
from optparse import make_option
import csv


class Command(BaseCommand):

    option_list = BaseCommand.option_list + (
        make_option('--csv', dest='csv', help='CSV Source File'),
    )

    def handle(self, *app_labels, **options):
        args = "Usage: ./manage.py convert_artstor_assets --csv filename"

        if 'csv' not in options or options['csv'] is None:
            print args
            return

        filename = options.get('csv')
        print "Importing data from: %s" % filename

        with open(filename, "rb") as f:
            reader = csv.reader(f, delimiter=",")
            for idx, line in enumerate(reader):
                try:
                    sources = Source.objects.filter(url=line[1])
                    for source in sources:
                        source.label = 'deprecated_image_fpx'
                        source.primary = False
                        source.save()

                        Source.objects.get_or_create(label="image_fpxid",
                                                     url=line[0],
                                                     primary=True,
                                                     height=source.height,
                                                     width=source.width,
                                                     size=source.size,
                                                     asset=source.asset)
                        print "%s: Asset %s converted %s to %s" % \
                            (idx, source.asset.id, line[1], line[0])

                except Source.DoesNotExist:
                    print "Unable to find %s" % line[1]
