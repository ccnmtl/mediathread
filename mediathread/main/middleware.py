import waffle
from courseaffils.middleware import CourseManagerMiddleware
from mediathread.main.views import MethCourseListView


class MethCourseManagerMiddleware(CourseManagerMiddleware):
    def process_request(self, request):
        r = super(MethCourseManagerMiddleware, self).process_request(
            request)
        if waffle.flag_is_active(request, 'course_activation') and \
           r is not None:
            r = MethCourseListView.as_view()(request)
        return r
