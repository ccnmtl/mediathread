from courseaffils.lib import in_course_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.http.response import HttpResponseNotAllowed, HttpResponse, \
    HttpResponseForbidden
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from mediathread.djangosherd.models import SherdNote
from mediathread.main.course_details import cached_course_is_faculty, \
    all_selections_are_visible
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


class RestrictedMaterialsMixin(object):

    def dispatch(self, *args, **kwargs):
        # initialize a few helpful variables here
        self.record_viewer = self.request.user

        self.record_owner = None
        record_owner_name = kwargs.pop('record_owner_name', None)
        if record_owner_name:
            self.record_owner = get_object_or_404(User,
                                                  username=record_owner_name)

        # Is the current user faculty or a CCNMTL staff member
        self.is_viewer_faculty = cached_course_is_faculty(self.request.course,
                                                          self.record_viewer)

        # Can the record_owner edit the records
        self.viewing_own_records = (self.record_owner == self.record_viewer)
        self.viewing_faculty_records = (
            self.record_owner and
            cached_course_is_faculty(self.request.course, self.record_owner))

        # Does the course allow viewing other user selections?
        # The viewer can always view their own records + faculty records
        # If the viewer is faculty, they can view all records
        self.all_selections_are_visible = \
            all_selections_are_visible(self.request.course)

        self.visible_authors = []
        if not self.all_selections_are_visible and not self.is_viewer_faculty:
            self.visible_authors = [self.record_viewer.id]  # me
            for user in self.request.course.faculty.all():
                self.visible_authors.append(user.id)

        return super(RestrictedMaterialsMixin, self).dispatch(*args, **kwargs)

    def visible_assets_and_notes(self, request, assets):
        tag_string = request.GET.get('tag', '')
        modified = request.GET.get('modified', '')
        vocabulary = dict((key[len('vocabulary-'):], val.split(","))
                          for key, val in request.GET.items()
                          if key.startswith('vocabulary-'))

        visible_notes = SherdNote.objects.get_related_notes(
            assets, self.record_owner or None, self.visible_authors,
            tag_string, modified, vocabulary)

        # return the related asset ids
        ids = visible_notes.values_list('asset__id', flat=True)
        visible_assets = assets.filter(id__in=ids).distinct()
        return (visible_assets, visible_notes)


class AjaxRequiredMixin(object):
    @method_decorator(ajax_required)
    def dispatch(self, *args, **kwargs):
        return super(AjaxRequiredMixin, self).dispatch(*args, **kwargs)


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
        if not self.request.user.is_staff:
            in_course_or_404(self.request.user.username, self.request.course)

        return super(LoggedInMixin, self).dispatch(*args, **kwargs)


class LoggedInFacultyMixin(object):
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        if not cached_course_is_faculty(self.request.course,
                                        self.request.user):
            return HttpResponseForbidden("forbidden")

        return super(LoggedInFacultyMixin, self).dispatch(*args, **kwargs)


class LoggedInMixinSuperuser(object):
    @method_decorator(user_passes_test(lambda u: u.is_superuser))
    def dispatch(self, *args, **kwargs):
        return super(LoggedInMixinSuperuser, self).dispatch(*args, **kwargs)
