from courseaffils.middleware import CourseManagerMiddleware, SESSION_KEY
from courseaffils.models import Course

from lti_auth.models import LTICourseContext
from mediathread.main.views import MethCourseListView


class MethCourseManagerMiddleware(CourseManagerMiddleware):
    def process_request(self, request):
        # LTI requests need to have the course set explicitly
        # particularly for the collection integration
        # 'context_id' comes through in the LTI POST request
        lti_course_id = request.POST.get('context_id', None)
        if lti_course_id is not None:
            try:
                ctx = LTICourseContext.objects.get(
                    lms_course_context=lti_course_id)

                course = Course.objects.get(group=ctx.group,
                                            faculty_group=ctx.faculty_group)
                request.session[SESSION_KEY] = course
                self.decorate_request(request, course)
                return None
            except LTICourseContext.DoesNotExist:
                # the course *should* exist, but don't break if it doesn't
                pass

        return super(MethCourseManagerMiddleware, self).process_request(
            request, MethCourseListView)
