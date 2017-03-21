from courseaffils.middleware import CourseManagerMiddleware
from mediathread.main.views import MethCourseListView


class MethCourseManagerMiddleware(CourseManagerMiddleware):
    def process_request(self, request):
        return super(MethCourseManagerMiddleware, self).process_request(
            request, MethCourseListView)
