from django import template
from django.template.defaultfilters import timesince
from djangohelpers.templatetags import TemplateTagNode
from mediathread.projects.models import Course, Project


register = template.Library()


class UserCourses(TemplateTagNode):
    noun_for = {"for": "user"}

    def __init__(self, varname, user):
        TemplateTagNode.__init__(self, varname, user=user)

    def execute_query(self, user):
        user_courses = Course.objects.filter(group__in=user.groups.all())
        return len(user_courses)
register.tag('num_courses', UserCourses.process_tag)


def timesince_approx(value, arg=None):
    return timesince(value, arg).split(',')[0]
register.filter(timesince_approx)


def assignment_responses(project, request):
    return project.responses(request)
register.filter(assignment_responses)


def discussions(project, request):
    return project.discussions(request)
register.filter(discussions)


def is_assignment(project, request):
    return ((isinstance(project, Project) and
             project.is_assignment(request)) or
            (isinstance(project, dict) and
             project['publish'] == 'Assignment'))
register.filter(is_assignment)


def project_type(project, request):
    if is_assignment(project, request):
        return "assignment"
    else:
        return "composition"
register.filter(project_type)
