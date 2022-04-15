import unicodecsv as csv
import json

from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.db import transaction
from django.db.models.query_utils import Q
from django.http.response import HttpResponseNotAllowed, HttpResponse, \
    HttpResponseForbidden
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
import reversion

from mediathread.djangosherd.models import SherdNote
from mediathread.main.course_details import cached_course_is_faculty, \
    all_selections_are_visible, all_items_are_visible, cached_course_is_member
from mediathread.projects.models import Project, ProjectNote
from mediathread.util import attach_course_to_request


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
    return wrap


def attach_course_request(func):
    """
    Attach course to the request, based on the url kwarg.
    """
    def wrap(request, *args, **kwargs):
        request = attach_course_to_request(request, **kwargs)
        kwargs.pop('course_pk', None)

        return func(request, *args, **kwargs)

    wrap.__doc__ = func.__doc__
    return wrap


def faculty_only(func):

    def wrap(request, *args, **kwargs):
        if request.user is None or request.user.is_anonymous:
            return HttpResponseForbidden("forbidden")
        if not cached_course_is_faculty(request.course, request.user):
            return HttpResponseForbidden("forbidden")
        return func(request, *args, **kwargs)

    wrap.__doc__ = func.__doc__
    return wrap


class RestrictedMaterialsMixin(object):

    def dispatch(self, *args, **kwargs):
        self.request = attach_course_to_request(self.request, **kwargs)

        record_owner_name = kwargs.pop('record_owner_name', None)
        self.initialize(record_owner_name)

        return super(RestrictedMaterialsMixin, self).dispatch(*args, **kwargs)

    def initialize(self, record_owner_name=None):
        # initialize a few helpful variables here
        self.record_viewer = self.request.user

        self.record_owner = None
        if record_owner_name:
            self.record_owner = get_object_or_404(
                User, username=record_owner_name)

        # Is the current user faculty or a CTL staff member
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
        self.all_items_are_visible = \
            all_items_are_visible(self.request.course)

        self.visible_authors = []
        if (not self.is_viewer_faculty and
                (not self.all_selections_are_visible or
                 not self.all_items_are_visible)):
            self.visible_authors = [self.record_viewer.id]  # me
            for user in self.request.course.faculty.all():
                self.visible_authors.append(user.id)

    def visible_assets_and_notes(self, request, assets):
        tag_string = request.GET.get('tag', '')
        modified = request.GET.get('modified', '')
        vocabulary = dict((key[len('vocabulary-'):], val.split(","))
                          for key, val in request.GET.items()
                          if key.startswith('vocabulary-'))

        visible_notes = SherdNote.objects.get_related_notes(
            assets, self.record_owner or None, self.visible_authors,
            self.all_items_are_visible, tag_string, modified, vocabulary)
        visible_notes = visible_notes.filter_by_media_type(
            request.GET.get('media_type'))

        if request.GET.getlist('primary_type[]'):
            filtered_types = request.GET.getlist('primary_type[]')
            visible_notes = visible_notes.exclude_primary_types(filtered_types)
        elif request.GET.get('primary_type'):
            # If primary_type is passed in as a string, use that
            # instead of the list.

            filtered_type = request.GET.get('primary_type')
            visible_notes = visible_notes.exclude_primary_types(
                [filtered_type])

        search_text = request.GET.get('search_text', '').strip().lower()
        if len(search_text) > 0:
            visible_notes = visible_notes.filter(
                Q(asset__title__icontains=search_text) |
                Q(title__icontains=search_text))

        # filter out notes associated with hidden project responses
        # (for selection assignment responses only right now)
        (visible, hidden) = Project.objects.responses_by_course(
            request.course, self.record_viewer)

        if len(hidden) > 0:
            pids = [project.id for project in hidden]
            pnotes = ProjectNote.objects.filter(project__id__in=pids)
            pnids = pnotes.values_list('annotation__id', flat=True)
            visible_notes = visible_notes.exclude(id__in=pnids)

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


class CSVResponseMixin():

    def render_csv_response(self, filename, headers, rows):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = \
            'attachment; filename=' + filename + '.csv'
        writer = csv.writer(response)

        writer.writerow(headers)

        for row in rows:
            try:
                writer.writerow(row)
            except csv.Error:
                pass
            except UnicodeEncodeError:
                pass

        return response


class LoggedInMixin(object):
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(LoggedInMixin, self).dispatch(*args, **kwargs)


class LoggedInCourseMixin(object):
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        self.request = attach_course_to_request(self.request, **kwargs)

        # This handles staff & true course members
        if not cached_course_is_member(self.request.course, self.request.user):
            return HttpResponseForbidden("forbidden")

        return super(LoggedInCourseMixin, self).dispatch(*args, **kwargs)


class LoggedInFacultyMixin(object):
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        self.request = attach_course_to_request(self.request, **kwargs)

        if not cached_course_is_faculty(self.request.course,
                                        self.request.user):
            return HttpResponseForbidden("forbidden")

        return super(LoggedInFacultyMixin, self).dispatch(*args, **kwargs)


class LoggedInSuperuserMixin(object):
    @method_decorator(user_passes_test(lambda u: u.is_superuser))
    def dispatch(self, *args, **kwargs):
        self.request = attach_course_to_request(self.request, **kwargs)

        return super(LoggedInSuperuserMixin, self).dispatch(*args, **kwargs)


class CreateReversionMixin(object):
    @transaction.atomic()
    @reversion.create_revision()
    def dispatch(self, *args, **kwargs):
        kwargs.pop('course_pk', None)
        return super(CreateReversionMixin, self).dispatch(*args, **kwargs)


class ProjectReadableMixin(object):
    def dispatch(self, *args, **kwargs):
        project = get_object_or_404(Project, pk=kwargs.get('project_id', None))
        if not project.can_read(self.request.course, self.request.user):
            return HttpResponseForbidden("forbidden")
        self.project = project
        return super(ProjectReadableMixin, self).dispatch(*args, **kwargs)


class ProjectEditableMixin(object):
    def dispatch(self, *args, **kwargs):
        project = get_object_or_404(Project, pk=kwargs.get('project_id', None))
        if (not project.can_edit(self.request.course, self.request.user)):
            return HttpResponseForbidden("forbidden")
        self.project = project
        return super(ProjectEditableMixin, self).dispatch(*args, **kwargs)
