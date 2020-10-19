from courseaffils.models import Course, CourseInfo
from django.conf import settings
from django.core.cache import cache
from panopto.session import PanoptoSessionManager

from mediathread.assetmgr.models import ExternalCollection
from structuredcollaboration.models import Collaboration


UPLOAD_PERMISSION_KEY = "upload_permission"
UPLOAD_PERMISSION_ADMINISTRATOR = 0
UPLOAD_PERMISSION_INSTRUCTOR = 1
UPLOAD_PERMISSION_STUDENT = 2

UPLOAD_PERMISSION_LEVELS = [(UPLOAD_PERMISSION_ADMINISTRATOR,
                            'Administrators Only'),
                            (UPLOAD_PERMISSION_INSTRUCTOR,
                            'Instructors and Administrators'),
                            (UPLOAD_PERMISSION_STUDENT,
                            'Students, Instructors and Administrators (All)')]

UPLOAD_PERMISSION_DEFAULT = UPLOAD_PERMISSION_INSTRUCTOR


def can_upload(user, course):
    value = int(course.get_detail(UPLOAD_PERMISSION_KEY,
                                  UPLOAD_PERMISSION_DEFAULT))
    if user.is_staff:
        return True
    elif (cached_course_is_faculty(course, user) and
            value >= UPLOAD_PERMISSION_INSTRUCTOR):
        return True
    elif value == UPLOAD_PERMISSION_STUDENT:
        return True
    else:
        return False


def get_uploader(course):
    return ExternalCollection.objects.filter(
        course=course, uploader=True).first()


def is_upload_enabled(course):
    return get_uploader(course) is not None


UPLOAD_FOLDER_KEY = "upload_folder"


def get_upload_folder(course):
    return course.get_detail(UPLOAD_FOLDER_KEY, '')


ALLOW_PUBLIC_COMPOSITIONS_KEY = "allow_public_compositions"
ALLOW_PUBLIC_COMPOSITIONS_DEFAULT = 0


def allow_public_compositions(course):
    value = int(course.get_detail(ALLOW_PUBLIC_COMPOSITIONS_KEY,
                                  ALLOW_PUBLIC_COMPOSITIONS_DEFAULT))
    return bool(value)


SELECTION_VISIBILITY_KEY = "selection_visibility"
SELECTION_VISIBILITY_DEFAULT = 1


def all_selections_are_visible(course):
    value = int(course.get_detail(SELECTION_VISIBILITY_KEY,
                                  SELECTION_VISIBILITY_DEFAULT))
    return bool(value)


ITEM_VISIBILITY_KEY = "item_visibility"
ITEM_VISIBILITY_DEFAULT = 1


def all_items_are_visible(course):
    value = int(course.get_detail(ITEM_VISIBILITY_KEY,
                                  ITEM_VISIBILITY_DEFAULT))
    return bool(value)


COURSE_INFORMATION_TITLE_KEY = "course_information_title"
COURSE_INFORMATION_TITLE_DEFAULT = "From Your Instructor"


def allow_item_download(course):
    try:
        value = int(course.get_detail(ALLOW_ITEM_DOWNLOAD_KEY,
                                      ALLOW_ITEM_DOWNLOAD_DEFAULT))
    except AttributeError:
        value = False

    return bool(value)


ALLOW_ITEM_DOWNLOAD_KEY = "allow_item_download"
ALLOW_ITEM_DOWNLOAD_DEFAULT = 0


def allow_roster_changes(course):
    value = int(course.get_detail(ALLOW_ROSTER_CHANGES_KEY,
                                  ALLOW_ROSTER_CHANGES_DEFAULT))
    return bool(value)


ALLOW_ROSTER_CHANGES_KEY = "allow_roster_changes"
ALLOW_ROSTER_CHANGES_DEFAULT = 1


def course_information_title(course):
    return course.get_detail(COURSE_INFORMATION_TITLE_KEY,
                             COURSE_INFORMATION_TITLE_DEFAULT)


def cached_course_is_member(course, user):
    key = "%s:%s:is_member" % (course.id, user.id)
    if key not in cache:
        cache.set(key, course.is_member(user))
    return cache.get(key)


def cached_course_is_faculty(course, user):
    key = "%s:%s:is_faculty" % (course.id, user.id)
    if key not in cache:
        cache.set(key, course.is_faculty(user))
    return cache.get(key)


def cached_course_collaboration(course):
    key = "%s:course:collaboration" % (course.id)
    the_collaboration = cache.get(key)
    if the_collaboration is None:
        try:
            the_collaboration = Collaboration.objects.get_for_object(course)
            cache.set(key, the_collaboration)
        except Collaboration.DoesNotExist:
            the_collaboration = None

    return the_collaboration


def get_guest_sandbox():
    return Course.objects.get(title="Mediathread Guest Sandbox")


def has_student_activity(course):
    """Returns True if the course has any student activity."""
    # TODO
    return True


def add_upload_folder(course):
    value = get_upload_folder(course)
    if value:
        return value

    return _add_panopto_folder(
        course, settings.PANOPTO_PARENT_FOLDER, UPLOAD_FOLDER_KEY)


def _add_panopto_folder(course, parent_folder_uuid, key):
    session_mgr = PanoptoSessionManager(
        settings.PANOPTO_SERVER, settings.PANOPTO_API_USER,
        instance_name=settings.PANOPTO_INSTANCE_NAME,
        password=settings.PANOPTO_API_PASSWORD)

    parent_folder = parent_folder_uuid
    try:
        term_year = course.info.termyear()
        if term_year:
            folder_id = session_mgr.get_folder(parent_folder_uuid, term_year)
            if folder_id:
                parent_folder = folder_id
    except CourseInfo.DoesNotExist:
        pass

    new_folder = session_mgr.get_folder(parent_folder, course.title)
    if len(new_folder) < 1:
        new_folder = session_mgr.add_folder(course.title, parent_folder)

    if len(new_folder) > 0:
        course.add_detail(key, new_folder)

    return new_folder
