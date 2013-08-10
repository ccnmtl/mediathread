from mediathread.api import TagResource
from mediathread.djangosherd.models import SherdNote
from tagging.models import Tag
UPLOAD_PERMISSION_KEY = "upload_permission"

UPLOAD_PERMISSION_ADMINISTRATOR = 0
UPLOAD_PERMISSION_INSTRUCTOR = 1
UPLOAD_PERMISSION_STUDENT = 2

UPLOAD_PERMISSION_LEVELS = [(UPLOAD_PERMISSION_ADMINISTRATOR, 'Administrator'),
                            (UPLOAD_PERMISSION_INSTRUCTOR, 'Instructor'),
                            (UPLOAD_PERMISSION_STUDENT, 'Student')]

UPLOAD_PERMISSION_DEFAULT = UPLOAD_PERMISSION_INSTRUCTOR


def can_upload(user, course):
    value = int(course.get_detail(UPLOAD_PERMISSION_KEY,
                                  UPLOAD_PERMISSION_DEFAULT))
    if user.is_staff:
        return True
    elif course.is_faculty(user) and value >= UPLOAD_PERMISSION_INSTRUCTOR:
        return True
    elif value == UPLOAD_PERMISSION_STUDENT:
        return True

ALLOW_PUBLIC_COMPOSITIONS_KEY = "allow_public_compositions"
ALLOW_PUBLIC_COMPOSITIONS_DEFAULT = 0


def allow_public_compositions(course):
    value = int(course.get_detail(ALLOW_PUBLIC_COMPOSITIONS_KEY,
                                  ALLOW_PUBLIC_COMPOSITIONS_DEFAULT))
    b = bool(value)
    return b

SELECTION_VISIBILITY_KEY = "selection_visibility"
SELECTION_VISIBILITY_DEFAULT = 1


def all_selections_are_visible(course):
    value = int(course.get_detail(SELECTION_VISIBILITY_KEY,
                                  SELECTION_VISIBILITY_DEFAULT))
    return bool(value)


def render_tags_by_course(request, record_owner):
    course = request.course
    logged_in_user = request.user

    # Is the current user faculty OR staff
    is_faculty = course.is_faculty(logged_in_user)

    # Can the record_owner edit the records
    viewing_own_records = (record_owner == logged_in_user)
    viewing_faculty_records = record_owner and course.is_faculty(record_owner)

    # Does the course allow viewing other user selections?
    owner_selections_are_visible = (
        all_selections_are_visible(course) or
        viewing_own_records or viewing_faculty_records or is_faculty)

    tags = []
    if record_owner:
        if owner_selections_are_visible:
            # Tags for selected user
            tags = Tag.objects.usage_for_queryset(
                record_owner.sherdnote_set.filter(asset__course=course),
                counts=True)
    else:
        if owner_selections_are_visible:
            # Tags for the whole class
            tags = Tag.objects.usage_for_queryset(
                SherdNote.objects.filter(asset__course=course),
                counts=True)
        else:
            # Tags for myself and faculty members
            tags = Tag.objects.usage_for_queryset(
                logged_in_user.sherdnote_set.filter(asset__course=course),
                counts=True)

            for f in course.faculty:
                tags.extend(Tag.objects.usage_for_queryset(
                            f.sherdnote_set.filter(asset__course=course),
                            counts=True))

    tags.sort(lambda a, b: cmp(a.name.lower(), b.name.lower()))

    return TagResource().render_list(request, tags)
