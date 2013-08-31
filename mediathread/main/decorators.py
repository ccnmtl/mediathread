from django.http import Http404, HttpResponseForbidden


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
            raise Http404()
        return func(request, *args, **kwargs)

    wrap.__doc__ = func.__doc__
    wrap.__name__ = func.__name__
    return wrap


def faculty_only(func):

    def wrap(request, *args, **kwargs):
        if not request.course.is_faculty(request.user):
            return HttpResponseForbidden("forbidden")
        return func(request, *args, **kwargs)

    wrap.__doc__ = func.__doc__
    wrap.__name__ = func.__name__
    return wrap
