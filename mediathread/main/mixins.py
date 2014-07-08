from courseaffils.lib import in_course_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http.response import HttpResponseNotAllowed, HttpResponse, \
    HttpResponseForbidden
from django.utils.decorators import method_decorator
from mediathread.main.course_details import cached_course_is_faculty
import json


def ajax_required(func):
    """
    AJAX request required decorator
    use it in your views:

    @ajax_required
    def my_view(request):
        ....

    """
    def wrap(request, *args, **kwargs):
        if not request.is_ajax():
            return HttpResponseNotAllowed("")
        return func(request, *args, **kwargs)

    wrap.__doc__ = func.__doc__
    wrap.__name__ = func.__name__
    return wrap


def faculty_only(func):

    def wrap(request, *args, **kwargs):
        if not cached_course_is_faculty(request.course, request.user):
            return HttpResponseForbidden("forbidden")
        return func(request, *args, **kwargs)

    wrap.__doc__ = func.__doc__
    wrap.__name__ = func.__name__
    return wrap


class CourseRequiredMixin(object):

    def dispatch(self, *args, **kwargs):
        if not self.request.user.is_staff:
            in_course_or_404(self.request.user.username, self.request.course)

        return super(CourseRequiredMixin, self).dispatch(*args, **kwargs)


class AjaxRequiredMixin(object):
    @method_decorator(ajax_required)
    def dispatch(self, *args, **kwargs):
        return super(JSONResponseMixin, self).dispatch(*args, **kwargs)


class JSONResponseMixin(object):
    def render_to_json_response(self, context, **response_kwargs):
        """
        Returns a JSON response, transforming 'context' to make the payload.
        """
        return HttpResponse(json.dumps(context, indent=2),
                            content_type='application/json',
                            **response_kwargs)


class LoggedInMixin(object):
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(LoggedInMixin, self).dispatch(*args, **kwargs)


class LoggedInMixinSuperuser(object):
    @method_decorator(user_passes_test(lambda u: u.is_superuser))
    def dispatch(self, *args, **kwargs):
        return super(LoggedInMixinSuperuser, self).dispatch(*args, **kwargs)
