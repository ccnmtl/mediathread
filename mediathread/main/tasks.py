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

    def get_course(self, session, course_string):
        d = CanvasTemplate.to_dict(course_string)
        s = WindTemplate.to_string(d)
        try:
            return Course.objects.get(group__name=s)
        except Course.DoesNotExist:
            self.log_message(
                None, session, ERROR,
                '{} ({}): No course matches {}'.format(
                    session['Name'], session['Id'], course_string))
            return None

    def get_author(self, course, uni):
        # If the student UNI is not yet in this course, add them as a student
        user, created = User.objects.get_or_create(username=uni)

        if not course.is_true_member(user):
            # @todo - determine if there is an api we could use to validate
            # a student's course membership
            course.group.user_set.add(user)
        return user, created

    def get_course_folder(self, course):
        course_folder_id = get_upload_folder(course)
        if not course_folder_id:
            self.log_message(
                course, None, ERROR,
                '{} course does not have upload enabled'.format(course.title))
        return course_folder_id

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

    def parse_description(self, session):
        try:
            description = session['Description'].lower().strip()
            pieces = description.split(',')
            assert len(pieces) == 2
            return pieces
        except (AttributeError, AssertionError):
            self.log_message(
                None, session, ERROR,
                '{} ({}) does not have a UNI and/or coursestring'.format(
                    session['Name'], session['Id']))
            return []

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
        # Get the destination folder
        course_folder_id = self.get_course_folder(course)
        if not course_folder_id:
            return

        session_mgr = self.get_session_manager()

        for session in session_mgr.get_session_list(ingest_folder_id):
            item = self.process_session(
                session_mgr, session, course, author, course_folder_id)

            # Craft a message about this session
            self.add_session_status(course, session, item, author, False)

    def automated_ingest(self):
        '''
            Periodically ingest videos within the identified Panopto folders.
            Course and author should be specified within each session's
            description. Once identified, the videos are associated with the
            course and author, then moved to the course's
            default upload folder. This runs as an hourly task.

            Videos within the common folder are expected to be uploaded with
                UNI,course_string
            in the video description.

            * UNI - is the student or faculty identifier
            * course_string - is the Canvas flavor of a course identifier, i.e.
                SOCWT7100_099_2020_3
        '''
        for bulk_folder_id in settings.PANOPTO_INGEST_FOLDERS:
            session_mgr = self.get_session_manager()

            for session in session_mgr.get_session_list(bulk_folder_id):
                # Get the uni & course_string from the video's description
                pieces = self.parse_description(session)
                if not pieces:
                    continue

                # Get the course from the course_string
                course = self.get_course(session, pieces[1])
                if not course:
                    continue

                # Get the destination folder for the course
                course_folder_id = self.get_course_folder(course)
                if not course_folder_id:
                    continue

                # Get the author via the UNI stashed in the session description
                # The author will be created and added to the course if needed
                author, created = self.get_author(course, pieces[0])

                item = self.process_session(
                    session_mgr, session, course, author, course_folder_id)

                # Craft a message about this session
                self.add_session_status(course, session, item, author, created)


@periodic_task(run_every=crontab(minute='*/10'))
def panopto_ingest():
    PanoptoIngester().automated_ingest()
