from celery.schedules import crontab
from celery.task.base import periodic_task
from courseaffils.columbia import CanvasTemplate, WindTemplate
from courseaffils.models import Course
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.messages.constants import ERROR, INFO, WARNING
from django.contrib.sites.shortcuts import get_current_site
from mediathread.assetmgr.models import Source, Asset
from mediathread.main.course_details import get_upload_folder
from mediathread.main.models import PanoptoIngestLogEntry
from mediathread.main.util import user_display_name, send_template_email
from panopto.session import PanoptoSessionManager


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

    def log_message(self, course, session, level, msg):
        if self.request is not None:
            messages.add_message(self.request, level, msg)
        else:
            PanoptoIngestLogEntry.objects.create(
                course=course, session_id=session['Id'],
                level=level, message=msg)

    def is_session_complete(self, course, session):
        complete = session['State'] == 'Complete'
        if not complete:
            msg = '{} ({}) incomplete'.format(session['Name'], session['Id'])
            self.log_message(course, session, ERROR, msg)
        return complete

    def is_already_imported(self, course, session):
        session_name = session['Name']
        session_id = session['Id']
        imported = Source.objects.filter(
            label='mp4_panopto', url=session_id).count() > 0
        if imported:
            self.log_message(
                course, session, WARNING,
                '{} ({}) already imported'.format(session_name, session_id))
        return imported

    def get_course(self, course_string):
        d = CanvasTemplate.to_dict(course_string)
        s = WindTemplate.to_string(d)
        try:
            return Course.objects.get(group__name=s)
        except Course.DoesNotExist:
            return None

    def get_author(self, course, uni):
        # If the student UNI is not yet in this course, add them as a student
        user, created = User.objects.get_or_create(username=uni)

        if not course.is_true_member(user):
            course.group.user_set.add(user)
        return user, created

    def add_session_status(self, course, session, item, author, created):
        msg = '{} ({}) saved as <a href="/asset/{}/">{}</a> for {}'.format(
            session['Name'], session['Id'], item.id,
            item.title, user_display_name(author))
        if created:
            msg = '{}. <b>{} is a new user</b>'.format(msg, author.username)
        self.log_message(course, session, INFO, msg)

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

    def parse_description(self, session_id, session_name, description):
        pieces = description.split(',')
        if len(pieces) != 2 or len(pieces[0]) < 1 or len(pieces[1]) < 1:
            return []

        return pieces

    def process_session(self, mgr, session, course, author, course_folder_id):
        if not self.is_session_complete(course, session):
            return
        if self.is_already_imported(course, session):
            return

        # Create a Mediathread Item for this session
        session_id = session['Id']
        item = self.create_item(
            course, session['Name'], author, session_id, session['ThumbUrl'])

        # Move the item to this course's folder
        mgr.move_sessions([session_id], course_folder_id)

        # Send an email to the student letting them know the video is ready
        self.send_email(course, author, item)

        return item

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

    def folder_ingest(self, course, author, ingest_folder_id):
        '''
            Ingest all videos within an identified Panopto folder.
            The passed author will own all ingested videos.
            This functionality is available to instructors within
            the Managed Course section of Mediathread.
        '''
        folder_id = get_upload_folder(course)
        session_mgr = self.get_session_manager()

        for session in session_mgr.get_session_list(ingest_folder_id):
            item = self.process_session(
                session_mgr, session, course, author, folder_id)

            # Craft a message about this session
            self.add_session_status(course, session, item, author, False)

    def automated_ingest(self):
        '''
            Ingest all videos within the Mediathread bulk ingest folder.
            Course and author are specified within each session's
            description. This runs as an hourly task
        '''
        folder_id = settings.PANOPTO_INGEST_FOLDER
        session_mgr = self.get_session_manager()

        for session in session_mgr.get_session_list(folder_id):
            uni, course_string = \
                self.parse_description(
                    session['Id'], session['Description'].lower().strip())

            # Get the course from the coursestring
            course = self.get_course(course_string)
            if not course:
                continue

            # Get the course destination folder
            course_folder_id = get_upload_folder(course)
            if not course_folder_id:
                continue

            # Get the author via the UNI stashed in the session description
            # The author will be created and added to the course if needed
            author, created = self.get_author(course, uni)

            item = self.process_session(
                session_mgr, session, course, author, course_folder_id)

            # Craft a message about this session
            self.add_session_status(course, session, item, author, created)


@periodic_task(run_every=crontab(hour="*", minute='0'))
def panopto_ingest():
    PanoptoIngester().automated_ingest()
