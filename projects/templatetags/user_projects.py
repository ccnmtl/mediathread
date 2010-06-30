from projects.models import Project

from django import template

from djangohelpers.templatetags import TemplateTagNode

class GetProjects(TemplateTagNode):

    noun_for = {"by":"author", "in":"course"}

    def __init__(self, varname, author, course):
        TemplateTagNode.__init__(self, varname, author=author, course=course)

    def execute_query(self, author, course):
        return Project.objects.filter(author=author,
                                      course=course,
                                      submitted=True)

register = template.Library()
register.tag('get_projects', GetProjects.process_tag)

from django.core.urlresolvers import reverse
@register.simple_tag
def active(request, pattern):

    yourspace_base = None
    if request.user.is_authenticated():
        yourspace_base = reverse('your-space', args=[request.user.username])

    if pattern == "Class Portal":
        if request.path == "/": #or request.path.startswith("/asset"):
            return 'active'

    if pattern == "Explore":
        if request.path.startswith('/explore'):
            return 'active'
    if pattern == "Class Analysis":
        if request.path == '/asset/':
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
