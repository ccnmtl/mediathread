from projects.models import Project
import re
from django import template

from djangohelpers.templatetags import TemplateTagNode
register = template.Library()

class GetProjects(TemplateTagNode):

    noun_for = {"by":"author", "in":"course", "for":"request"}

    def __init__(self, varname, author, course, request):
        TemplateTagNode.__init__(self, varname, author=author, course=course, request=request)

    def execute_query(self, author, course, request):
        return [p for p in Project.get_user_projects(author, course).filter(submitted=True)
                if p.visible(request)]


register.tag('get_projects', GetProjects.process_tag)

class GetCourseProjects(TemplateTagNode):

    noun_for = {"in":"course", "for":"request"}

    def __init__(self, varname, course, request):
        TemplateTagNode.__init__(self, varname, course=course, request=request)

    def execute_query(self, course, request):
        return [p for p in Project.objects.filter(course=course,
                                                  submitted=True).order_by('title')
                if p.visible(request)]


register.tag('get_course_projects', GetCourseProjects.process_tag)


from django.core.urlresolvers import reverse
@register.simple_tag
def active(request, pattern):

    yourspace_base = None
    if request.user.is_authenticated():
        yourspace_base = '/yourspace/%s/' % (request.user.username)
    if pattern == "Class Portal" or pattern == "Home":
        if request.path == "/":
            return 'active'
    if pattern == "Notifications":
        if request.path == "/notifications/": 
            return 'active'    
    if pattern == "Explore":
        if request.path.startswith('/explore'):
            return 'active'
    if pattern == "Class Analysis":
        if request.path == '/asset/':
            return 'active'
    if pattern == "Instructor":
        if request.path.startswith('/reports/'):
            return 'active'

    if pattern == "Analysis":
        if request.path == '/asset/' or re.match('/yourspace/',request.path):
            return 'active'

    if pattern == 'Your Items' or pattern == 'Your Projects':
        if yourspace_base is not None:
            if pattern == 'Your Items':
                if yourspace_base+'asset/' in request.path:
                    return 'active'
            if pattern == 'Your Projects':
                if yourspace_base+'project/' in request.path:
                    return 'active'
    return ''

class UserCourses(TemplateTagNode):
    noun_for = {"for": "user"}

    def __init__(self, varname, user):
        TemplateTagNode.__init__(self, varname, user=user)

    def execute_query(self, user):
        from projects.models import Course
        user_courses = Course.objects.filter(group__in=user.groups.all())
        return len(user_courses)
register.tag('num_courses', UserCourses.process_tag)


from django.template.defaultfilters import timesince
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
    return (isinstance(project, Project) and project.is_assignment(request)) or (isinstance(project, dict) and project['publish'] == 'Assignment')
register.filter(is_assignment)

