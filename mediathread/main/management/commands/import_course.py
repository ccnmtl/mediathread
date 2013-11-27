from courseaffils.models import Course
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from mediathread.assetmgr.models import Asset, Source
from mediathread.djangosherd.models import SherdNote
from optparse import make_option
import json


class Command(BaseCommand):

    option_list = BaseCommand.option_list + (
        make_option('--json', dest='json_file',
                    help='JSON file containing course assets'),
        make_option('--course-id', dest='course_id',
                    help='Destination course for data'),
    )

    def handle(self, *app_labels, **options):
        args = 'Usage: python manage.py import_course --json json file \
            --course-id destination course'

        if (not options.get('json_file') or
                not options.get('course_id')):
            print args
            return

        json_file = options.get('json_file')
        course_id = int(options.get('course_id'))

        course = Course.objects.get(id=course_id)
        print "Import %s into %s?" % (json_file, course.title)
        answer = raw_input("Continue? (yes/no) ")
        if answer == "no":
            print "Exiting"
            return

        print "Importing %s into %s" % (json_file, course.title)
        self.import_course_data(options.get('json_file'), course)

    def import_course_data(self, json_file, course):
        raw_data = open(json_file)
        json_data = json.load(raw_data)

        for asset_data in json_data['asset_set']:
            # Create asset
            author = User.objects.get(
                username=asset_data["author"]["username"])
            asset = Asset(author=author,
                          title=asset_data["title"],
                          course=course)

            asset.metadata_blob = asset_data["metadata_blob"]
            asset.save()

            # Add sources
            for key, value in asset_data["sources"].items():
                source_data = asset_data["sources"][key]
                source = Source(asset=asset,
                                label=source_data["label"],
                                url=source_data["url"],
                                primary=source_data["primary"],
                                media_type=source_data["media_type"],
                                size=source_data["size"],
                                height=source_data["height"],
                                width=source_data["width"])
                source.save()

            # Recreate annotations
            for ann_data in asset_data["annotations"]:
                ann_author = User.objects.get(
                    username=ann_data["author"]["username"])
                if ann_data["is_global_annotation"]:
                    ann = asset.global_annotation(ann_author, True)
                else:
                    ann = SherdNote(asset=asset,
                                    author=ann_author)

                ann.range1 = ann_data["range1"]
                ann.range2 = ann_data["range2"]
                ann.annotation_data = ann_data["annotation_data"]
                ann.title = ann_data["title"]

                tags = ""
                for tag in ann_data["metadata"]["tags"]:
                    tags = tags + "," + tag["name"]
                ann.tags = tags
                ann.body = ann_data["metadata"]["body"]
                ann.save()
