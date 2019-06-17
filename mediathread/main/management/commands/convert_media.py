from datetime import datetime

from courseaffils.models import Course
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from mediathread.assetmgr.models import Source
from mediathread.main.views import CourseConvertMaterialsView


class Command(BaseCommand):

    help = 'Migrate h264 streaming videos to Panopto'

    def add_arguments(self, parser):
        parser.add_argument('-uni', '--uni')
        parser.add_argument('-f', '--fake', action='store_true')
        parser.add_argument('-n', '--number', default=1,
                            help='Number of courses to process')

    def get_courses(self):
        invalid_labels = ['mp4_panopto', 'image_fpx', 'image_fpxid', 'image']
        qs = Source.objects.filter(
            primary=True, asset__metadata_blob__contains='wardenclyffe-id',
            asset__added__gte=datetime(2014, 9, 1)).exclude(
                label__in=invalid_labels)
        ids = qs.values_list('asset__course__id', flat=True).distinct()
        return Course.objects.filter(id__in=ids).order_by('-created_at')

    def handle(self, *app_labels, **options):
        n = options['number']
        fake = options['fake']
        user = User.objects.get(username=options['uni'])

        view = CourseConvertMaterialsView()
        (url, secret) = view.get_conversion_endpoint()
        if not url:
            print(u'Conversion endpoint is not configured')
            return

        # Find courses that need to have assets converted
        courses = self.get_courses()[:n]
        for course in courses:
            folder = view.get_upload_folder(course)
            if folder and not fake:
                view.convert_course_media(user, course, url, secret, folder)
                print('Course {} media submitted'.format(course.id))
