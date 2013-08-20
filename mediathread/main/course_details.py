from mediathread.api import TagResource
from mediathread.djangosherd.models import SherdNote
from tagging.models import Tag
from django.core.cache import cache


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


def render_tags_by_course(request):
    course = request.course
    logged_in_user = request.user

    if (all_selections_are_visible(course) or
            cached_course_is_faculty(course, logged_in_user)):
        # Tags for the whole class
        tags = Tag.objects.usage_for_queryset(
            SherdNote.objects.filter(asset__course=course))
    else:
        # Show only tags for myself and faculty members
        tags = Tag.objects.usage_for_queryset(
            logged_in_user.sherdnote_set.filter(asset__course=course))

        for f in course.faculty:
            tags.extend(Tag.objects.usage_for_queryset(
                        f.sherdnote_set.filter(asset__course=course)))

    tags.sort(lambda a, b: cmp(a.name.lower(), b.name.lower()))
    return TagResource().render_list(request, tags)


def cached_course_is_member(course, user):
    key = "%s:%s:is_member" % (course.id, user.id)
    if not key in cache:
        cache.set(key, course.is_member(user), 3)
    return cache.get(key)


def cached_course_is_faculty(course, user):
    key = "%s:%s:is_faculty" % (course.id, user.id)
    if not key in cache:
        cache.set(key, course.is_faculty(user), 3)
    return cache.get(key)
