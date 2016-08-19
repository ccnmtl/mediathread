from courseaffils.middleware import CourseManagerMiddleware, SESSION_KEY
from courseaffils.models import Course

from lti_auth.models import LTICourseContext
from mediathread.main.views import MethCourseListView


class MethCourseManagerMiddleware(CourseManagerMiddleware):
    def process_request(self, request):
        override_view = None

        # 'custom_course_context' comes through from lti. set the course.
        uuid = request.GET.get('custom_course_context', None)
        if uuid is not None:
            ctx = LTICourseContext.objects.get(uuid=uuid)
            course = Course.objects.get(group=ctx.group,
                                        faculty_group=ctx.faculty_group)
            request.session[SESSION_KEY] = course
            self.decorate_request(request, course)
            return None

        override_view = MethCourseListView

        return super(MethCourseManagerMiddleware, self).process_request(
            request, override_view)
