from courseaffils.models import Course
from django.shortcuts import get_object_or_404


def cmp(a, b):
    return (a > b) - (a < b)


def attach_course_to_request(request, **kwargs):
    """
    Looks up the course and attaches it to the given request, if
    possible.

    Returns the updated request object.
    """
    if not request.course:
        # Get the course from the URL if it exists.
        course_pk = kwargs.get('course_pk')
        if course_pk:
            course = get_object_or_404(Course, pk=course_pk)
            request.course = course

    return request
