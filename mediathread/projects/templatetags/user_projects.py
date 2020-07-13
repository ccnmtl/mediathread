from django import template
from django.db.models import Q
from djangohelpers.templatetags import TemplateTagNode
from mediathread.projects.models import Course, PUBLISHED


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
def published_assignment_responses(project):
    return project.collaboration.first().children.filter(
        policy_record__policy_name__in=PUBLISHED).count()


@register.simple_tag
def my_assignment_responses(project, user):
    return project.collaboration.first().children.filter(
        Q(project__author=user) | Q(project__participants=user)).distinct()
