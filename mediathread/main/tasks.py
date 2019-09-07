from courseaffils.models import Course
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.messages.constants import ERROR, INFO, WARNING
from django.contrib.sites.shortcuts import get_current_site
from panopto.session import PanoptoSessionManager

from mediathread.assetmgr.models import Source, Asset
from mediathread.main.course_details import (
    get_upload_folder, get_ingest_folder)
from mediathread.main.util import user_display_name, send_template_email


# from celery.decorators import periodic_task
# from celery.task.schedules import crontab
class PanoptoIngester(object):

    def __init__(self, request=None):
        self.request = request

    def get_session_manager(self):
        return PanoptoSessionManager(
            getattr(settings, 'PANOPTO_SERVER', None),
            getattr(settings, 'PANOPTO_API_USER', None),
            instance_name=getattr(settings, 'PANOPTO_INSTANCE_NAME', None),
            password=getattr(settings, 'PANOPTO_API_PASSWORD', None),
            cache_dir=getattr(settings, 'ZEEP_CACHE_DIR', None))

    def log_message(self, level, msg):
        if self.request is not None:
            messages.add_message(self.request, level, msg)
        else:
            print(msg)

    def is_session_complete(self, session):
        complete = session['State'] == 'Complete'
        if not complete:
            msg = '{} ({}) incomplete'.format(session['Name'], session['Id'])
            self.log_message(ERROR, msg)
        return complete

    def is_description_valid(self, session):
        valid = ('Description' in session and
                 session['Description'] and
                 len(session['Description']) > 0)
        if not valid:
            msg = '{} ({}) has no UNI specified'.format(
                session['Name'], session['Id'])
            self.log_message(ERROR, msg)
        return valid

    def is_already_imported(self, session):
        session_name = session['Name']
        session_id = session['Id']
        imported = Source.objects.filter(
            label='mp4_panopto', url=session_id).count() > 0
        if imported:
            self.log_message(
                INFO,
                '{} ({}) already imported'.format(session_name, session_id))
        return imported

    def get_author(self, course, uni):
        # If the student UNI is not yet in this course, add them as a student
        user, created = User.objects.get_or_create(username=uni)

        if not course.is_true_member(user):
            course.group.user_set.add(user)
        return user, created

    def create_item(self, course, name, author, session_id, thumb_url):
        # Create a Mediathread item using Session Name as the Item Title
        # and the Session Description as the Student UNI
        asset = Asset.objects.create(
            course=course, title=name, author=author)
        asset.save_tag(author, 'panopto import')
        Source.objects.create(
            asset=asset, primary=True, label='mp4_panopto', url=session_id)

        turl = 'https://{}{}'.format(settings.PANOPTO_SERVER, thumb_url)
        Source.objects.create(
            asset=asset, primary=False, label='thumb', url=turl)
        asset.global_annotation(author, auto_create=True)
        return asset

    def add_session_status(self, session, item, author, created):
        msg = '{} ({}) saved as <a href="/asset/{}/">{}</a> for {}'.format(
            session['Name'], session['Id'], item.id,
            item.title, user_display_name(author))
        if created:
            msg = '{}. <b>{} is a new user</b>'.format(msg, author.username)
        self.log_message(INFO, msg)

    def send_email(self, course, author, item):
        data = {
            'course': course,
            'domain': get_current_site(self.request).domain,  # @todo FIX
            'item': item
        }

        email_address = (author.email or
                         '{}@columbia.edu'.format(author.username))

        send_template_email(
            'Mediathread submission now available',
            'main/mediathread_submission.txt',
            data, email_address)

    def ingest_sessions(self, course, ingest_folder_id):
        course_folder_id = get_upload_folder(course)
        session_mgr = self.get_session_manager()

        for session in session_mgr.get_session_list(ingest_folder_id):
            if not self.is_session_complete(session):
                continue
            if self.is_already_imported(session):
                continue
            if not self.is_description_valid(session):
                continue

            # Get the author via the UNI stashed in the session description
            author, created = \
                self.get_author(course, session['Description'].lower().strip())

            # Create a Mediathread Item for this session
            session_id = session['Id']
            item = self.create_item(
                course, session['Name'], author, session_id,
                session['ThumbUrl'])

            # Move the item to this course's folder
            session_mgr.move_sessions([session_id], course_folder_id)

            # Craft a message about this session
            self.add_session_status(session, item, author, created)

            # Send an email to the student letting them know the video is ready
            self.send_email(course, author, item)

    def get_courses(self):
        return Course.objects.filter(
            coursedetails__name='ingest_folder',
            coursedetails__value__isnull=False).exclude(
                coursedetails__value__exact='')

    def ingest(self):
        for course in self.get_courses():
            try:
                self.ingest_sessions(course, get_ingest_folder(course))
            except Course.DoesNotExist:
                msg = 'No matching course found for {}'.format(course.name)
                self.add_message(WARNING, msg)


# @periodic_task(run_every=crontab(hour="*", minute="*", day_of_week="*"))
# def panopto_ingest():
#     print('Hourly Panopto Ingest Task')
#
#     PanoptoIngester().ingest()
