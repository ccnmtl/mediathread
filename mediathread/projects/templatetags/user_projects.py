from django import template
from django.conf import settings
from django.db.models import Q
from djangohelpers.templatetags import TemplateTagNode
from mediathread.projects.models import Course, PUBLISHED
from threadedcomments.models import ThreadedComment


register = template.Library()


class UserCourses(TemplateTagNode):
    noun_for = {"for": "user"}

    def __init__(self, varname, user):
        TemplateTagNode.__init__(self, varname, user=user)

    def execute_query(self, user):
        return Course.objects.filter(group__in=user.groups.all()).count()


register.tag('num_courses', UserCourses.process_tag)


@register.filter(name='assignment_responses')
def assignment_responses(project, request):
    return project.responses(request.course, request.user)


@register.simple_tag
def published_assignment_responses(assignment):
    if assignment.is_discussion_assignment():
        discussion = assignment.course_discussion()
        qs = ThreadedComment.objects.filter(
            content_type__model='collaboration',
            object_pk=discussion.content_object.pk,
            site__pk=settings.SITE_ID)
        qs = qs.exclude(user__groups=assignment.course.faculty_group)
        return qs.values('user').distinct().count()
    else:
        # Assumes the requester is an instructor
        return assignment.collaboration.first().children.filter(
            policy_record__policy_name__in=PUBLISHED).count()


@register.simple_tag
def my_assignment_responses(project, user):
    return project.collaboration.first().children.filter(
        Q(project__author=user) | Q(project__participants=user)).distinct()


@register.simple_tag
def comment_count(project, user):
    if not project.is_discussion_assignment():
        return (0, None)

    try:
        discussion = project.course_discussion()
        qs = ThreadedComment.objects.filter(
            content_type__model='collaboration',
            object_pk=discussion.content_object.pk,
            site__pk=settings.SITE_ID, user=user)
        return (qs.count(), qs.order_by('-submit_date').first().submit_date)
    except AttributeError:
        return (0, None)


@register.simple_tag
def student_response(responses, user):
    for response in responses:
        if user in response.attribution_list():
            return response
    return None


@register.filter
def date_format_change(date):
    if "hours" in date or "hour" in date:
        return date.replace('hours', 'hrs').replace('minutes', 'mins').replace(
            'hour', 'hr').replace('minute', 'min')
    elif "weeks" in date or "week" in date:
        return date.replace('weeks', 'w').replace('days', 'd').replace(
            'day', 'd').replace('week', 'w').replace('day', 'd')
