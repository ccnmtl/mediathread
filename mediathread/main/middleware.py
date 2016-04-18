import waffle
from courseaffils.middleware import CourseManagerMiddleware
from mediathread.main.views import HomepageView


class MethCourseManagerMiddleware(CourseManagerMiddleware):
    def process_request(self, request):
        r = super(MethCourseManagerMiddleware, self).process_request(
            request)
        if waffle.flag_is_active(request, 'instructor_homepage') and \
           r is not None:
            r = HomepageView.as_view()(request)
        return r
