import waffle
from courseaffils.middleware import CourseManagerMiddleware
from mediathread.main.views import MethCourseListView


class MethCourseManagerMiddleware(CourseManagerMiddleware):
    def process_request(self, request):
        override_view = None

        # When course_activation is turned on, use the MethCourseListView
        # which has the course activation feature instead of courseaffils'
        # CourseListView.
        if waffle.flag_is_active(request, 'course_activation'):
            override_view = MethCourseListView

        return super(MethCourseManagerMiddleware, self).process_request(
            request, override_view)
