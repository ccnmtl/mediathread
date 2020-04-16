from courseaffils.middleware import CourseManagerMiddleware, SESSION_KEY
from courseaffils.models import Course
from django.shortcuts import get_object_or_404

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

        # Don't display the switch course view when making an ajax
        # request that contains the 'course' GET param. Ultimately,
        # the course_list_view() part of this middleware should be
        # removed, or at least be changed to a simpler redirect-style
        # override.
        course_id = request.GET.get('course')
        if course_id:
            course = get_object_or_404(Course, pk=course_id)
            request.course = course
            self.decorate_request(request, course)
            return None

        return super(MethCourseManagerMiddleware, self).process_request(
            request, MethCourseListView)
