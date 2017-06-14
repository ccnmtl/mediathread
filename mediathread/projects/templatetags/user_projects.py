from django import template
from djangohelpers.templatetags import TemplateTagNode
from mediathread.projects.models import Course


register = template.Library()


class UserCourses(TemplateTagNode):
    noun_for = {"for": "user"}

    def __init__(self, varname, user):
        TemplateTagNode.__init__(self, varname, user=user)

    def execute_query(self, user):
        return Course.objects.filter(group__in=user.groups.all()).count()


register.tag('num_courses', UserCourses.process_tag)


def assignment_responses(project, request):
    return project.responses(request.course, request.user)


register.filter(assignment_responses)
