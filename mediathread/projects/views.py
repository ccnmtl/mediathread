from datetime import datetime
import json

from courseaffils.lib import get_public_name
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.core.paginator import Paginator
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect, \
    HttpResponseForbidden
from django.shortcuts import get_object_or_404
from django.template import RequestContext, loader
from django.template.defaultfilters import slugify
from django.views.generic.base import View, TemplateView
from djangohelpers.lib import allow_http
from reversion.models import Version

from mediathread.api import CourseResource
from mediathread.api import UserResource
from mediathread.assetmgr.api import AssetResource
from mediathread.assetmgr.models import Asset
from mediathread.discussions.views import threaded_comment_json
from mediathread.djangosherd.models import SherdNote, DiscussionIndex
from mediathread.main.course_details import allow_public_compositions
from mediathread.main.models import UserSetting
from mediathread.mixins import (
    LoggedInCourseMixin, RestrictedMaterialsMixin, AjaxRequiredMixin,
    JSONResponseMixin, LoggedInFacultyMixin, ProjectReadableMixin,
    ProjectEditableMixin, CreateReversionMixin)
from mediathread.projects.api import ProjectResource
from mediathread.projects.forms import ProjectForm
from mediathread.projects.generic.views import AssignmentView, \
    AssignmentEditView
from mediathread.projects.models import (
    Project, ProjectNote, PUBLISH_DRAFT, PROJECT_TYPE_SEQUENCE_ASSIGNMENT)
from mediathread.taxonomy.api import VocabularyResource
from mediathread.taxonomy.models import Vocabulary
from structuredcollaboration.models import Collaboration


class ProjectCreateView(LoggedInCourseMixin, JSONResponseMixin,
                        CreateReversionMixin, View):

    def get_title(self):
        title = self.request.POST.get('title', Project.DEFAULT_TITLE)
        if len(title) < 1:
            title = Project.DEFAULT_TITLE
        return title

    def format_date(self, due_date):
        formatted = None
        if due_date and len(due_date) > 0:
            # convert mm/dd/yyyy into a datetime
            formatted = datetime.strptime(due_date, '%m/%d/%Y')
        return formatted

    def get_confirmation_message(self, policy):
        if policy == PUBLISH_DRAFT[0]:
            return ('<strong>Complete</strong>! Your assignment has '
                    'been saved as <strong>Draft</strong>.')
        else:
            return ('<strong>Complete</strong>! Your assignment has been '
                    '<strong>published to the course</strong>.')

    def post(self, request):
        project_type = request.POST.get('project_type', 'composition')
        body = request.POST.get('body', '')
        response_policy = request.POST.get('response_view_policy', 'always')
        due_date = self.format_date(self.request.POST.get('due_date', None))
        instructions1 = self.request.POST.get('custom_instructions_1', None)
        instructions2 = self.request.POST.get('custom_instructions_2', None)
        summary = self.request.POST.get('summary', None)
        project = Project.objects.create(
            author=request.user, course=request.course, title=self.get_title(),
            project_type=project_type, response_view_policy=response_policy,
            body=body, due_date=due_date, custom_instructions_1=instructions1,
            custom_instructions_2=instructions2, summary=summary)

        project.participants.add(request.user)

        item_id = request.POST.get('item', None)
        project.create_or_update_item(item_id)

        policy = request.POST.get('publish', PUBLISH_DRAFT[0])
        collaboration = project.create_or_update_collaboration(policy)

        DiscussionIndex.update_class_references(
            project.body, None, None, collaboration, project.author)

        parent_id = request.POST.get('parent', None)
        project.set_parent(parent_id)

        if project_type == PROJECT_TYPE_SEQUENCE_ASSIGNMENT:
            messages.add_message(request, messages.SUCCESS,
                                 self.get_confirmation_message(policy))

        if not request.is_ajax():
            return HttpResponseRedirect(project.get_absolute_url())
        else:
            is_faculty = request.course.is_faculty(request.user)
            can_edit = project.can_edit(request.course, request.user)

            resource = ProjectResource(record_viewer=request.user,
                                       is_viewer_faculty=is_faculty,
                                       editable=can_edit)
            project_context = resource.render_one(request, project)
            project_context['editing'] = True

            data = {'panel_state': 'open',
                    'template': 'project',
                    'context': project_context}

            return self.render_to_json_response(data)


class ProjectSaveView(LoggedInCourseMixin, AjaxRequiredMixin,
                      JSONResponseMixin, ProjectEditableMixin,
                      CreateReversionMixin, View):

    def post(self, request, *args, **kwargs):
        frm = ProjectForm(request, instance=self.project, data=request.POST)
        if frm.is_valid():
            policy = request.POST.get('publish', PUBLISH_DRAFT[0])
            if policy == PUBLISH_DRAFT[0]:
                frm.instance.date_submitted = None
            else:
                frm.instance.date_submitted = datetime.now()

            frm.instance.author = request.user
            project = frm.save()

            project.participants.add(request.user)

            item_id = request.POST.get('item', None)
            project.create_or_update_item(item_id)

            # update the collaboration
            collaboration = project.create_or_update_collaboration(policy)
            DiscussionIndex.update_class_references(
                project.body, None, None, collaboration, project.author)

            parent_id = request.POST.get('parent', None)
            project.set_parent(parent_id)

            ctx = {
                'status': 'success',
                'is_essay_assignment': project.is_essay_assignment(),
                'title': project.title,
                'context': {
                    'project': {
                        'url': project.get_absolute_url()
                    }
                },
                'revision': {
                    'id': project.latest_version(),
                    'public_url': project.public_url(),
                    'visibility': project.visibility_short(),
                    'due_date': project.get_due_date()
                }
            }
        else:
            ctx = {'status': 'error', 'msg': ""}
            for key, value in frm.errors.items():
                if key == '__all__':
                    ctx['msg'] = ctx['msg'] + value[0] + "\n"
                else:
                    ctx['msg'] = \
                        '%s "%s" is not valid for the %s field.\n %s\n' % \
                        (ctx['msg'], frm.data[key],
                         frm.fields[key].label,
                         value[0].lower())

        return self.render_to_json_response(ctx)


class ProjectDeleteView(LoggedInCourseMixin, ProjectEditableMixin, View):
    def post(self, request, *args, **kwargs):
        """
        Delete the requested project. Regular access conventions apply.
        If the logged-in user is not allowed to delete
        the project, an HttpResponseForbidden
        will be returned
        """
        collaboration = self.project.get_collaboration()
        collaboration.remove_children()
        self.project.delete()
        collaboration.delete()
        return HttpResponseRedirect('/')


class UnsubmitResponseView(LoggedInFacultyMixin, CreateReversionMixin, View):

    def post(self, request, *args, **kwargs):
        project_id = request.POST.get('student-response', None)
        project = get_object_or_404(Project, id=project_id)

        assignment = project.assignment()
        if (not project.can_read(self.request.course, self.request.user) or
                not assignment):
            return HttpResponseForbidden("forbidden")

        project.date_submitted = None
        project.save()

        policy = 'PrivateEditorsAreOwners'
        project.create_or_update_collaboration(policy)

        return HttpResponseRedirect(
            reverse('project-workspace', kwargs={'project_id': assignment.id}))


class UpdateVisibilityView(LoggedInCourseMixin, ProjectEditableMixin,
                           CreateReversionMixin, View):

    def post(self, request, *args, **kwargs):
        policy = request.POST.get('publish', None)

        if policy is None:
            return HttpResponseForbidden('Must specify publish policy')

        self.project.create_or_update_collaboration(policy)

        return HttpResponseRedirect(
            reverse('project-workspace',
                    kwargs={'project_id': self.project.id}))


@login_required
def project_revisions(request, project_id):
    project = get_object_or_404(Project, pk=project_id, course=request.course)

    if not project.is_participant(request.user):
        return HttpResponseForbidden("forbidden")

    data = {'revisions': []}
    fmt = "%m/%d/%y %I:%M %p"
    for v in project.versions():
        author = User.objects.get(id=v.field_dict['author'])
        data['revisions'].append({
            'version_number': v.revision_id,
            'versioned_id': v.object_id,
            'author': get_public_name(author, request),
            'modified': v.revision.date_created.strftime(fmt)
        })

    return HttpResponse(json.dumps(data, indent=2),
                        content_type='application/json')


class ProjectPublicView(View):

    def dispatch(self, request, *args, **kwargs):
        context_slug = self.kwargs.get('context_slug', None)
        obj_id = self.kwargs.get('obj_id', None)

        context = get_object_or_404(Collaboration, slug=context_slug)
        request.collaboration_context = context
        collab = get_object_or_404(
            Collaboration,
            context=context,
            content_type=ContentType.objects.get(model='project'),
            object_pk=obj_id)

        if not collab.permission_to('read', request.course, request.user):
            return HttpResponseForbidden('forbidden')

        project_id = int(collab.object_pk)
        project = Project.objects.get(id=project_id)
        parent = project.assignment()
        if (project.is_selection_assignment() or
                (parent and parent.is_selection_assignment())):
            return HttpResponseForbidden('forbidden')
        elif (project.is_sequence_assignment() or
                (parent and parent.is_sequence_assignment())):
            return SequenceAssignmentReadOnlyView.as_view()(
                request, project_id=project_id)
        else:
            return ProjectReadOnlyView.as_view()(
                request, project_id=project_id)


class SequenceAssignmentReadOnlyView(ProjectReadableMixin, TemplateView):
    template_name = 'projects/sequence_assignment_view.html'

    def get_context_data(self, project_id):
        return {
            'is_faculty': False,
            'read_only_view': True,
            'assignment': self.project.assignment(),
            'assignment_can_edit': False,
            'my_response': None,
            'the_response': self.project,
            'response_can_edit': False,
            'responses': [],
            'feedback': None,
            'feedback_count': 0
        }


class ProjectReadOnlyView(ProjectReadableMixin, JSONResponseMixin,
                          TemplateView):
    """
    A single panel read-only view of the specified project/version combination.
    No assignment, response or feedback access/links.
    Regular access conventions apply. For example, if the project is "private"
    an HTTPResponseForbidden will be returned.

    Used for reviewing old project versions and public project access.

    Keyword arguments:
    project_id -- the model id
    version_number -- a specific project version or
    None for the current version

    """

    template_name = 'projects/project.html'

    def get(self, request, project_id, version_number=None):
        """
        A single panel read-only view of the specified project/version combo.
        No assignment, response or feedback access/links.
        Regular access conventions apply. For example, if the project is
        "private" an HTTPResponseForbidden will be returned.

        Used for reviewing old project versions and public project access.

        Keyword arguments:
        project_id -- the model id
        version_number -- a specific project version or
        None for the current version

        """

        project = get_object_or_404(Project, pk=project_id)

        data = {'space_owner': request.user.username}

        if not request.is_ajax():
            course = request.course
            if not course:
                public_url = project.public_url()
            else:
                # versioned view
                public_url = reverse('project-view-readonly',
                                     kwargs={'project_id': project.id,
                                             'version_number': version_number})

            data['project'] = project
            data['version'] = version_number
            data['public_url'] = public_url
            return self.render_to_response(data)
        else:
            if version_number:
                version = get_object_or_404(Version,
                                            object_id=str(project.id),
                                            revision_id=version_number)
                project = version.object_version.object

            panels = []

            is_faculty = (self.request.course and
                          self.request.course.is_faculty(request.user))

            # Requested project, either assignment or composition
            request.public = True

            resource = ProjectResource(record_viewer=request.user,
                                       is_viewer_faculty=False,
                                       editable=False)
            project_context = resource.render_one(request, project,
                                                  version_number)
            panel = {'panel_state': 'open',
                     'panel_state_label': "Version View",
                     'context': project_context,
                     'is_faculty': is_faculty,
                     'template': 'project'}
            panels.append(panel)

            data['panels'] = panels

            return self.render_to_json_response(data)


class SelectionAssignmentEditView(AssignmentEditView):
    template_name = 'projects/selection_assignment_edit.html'


class SequenceAssignmentEditView(AssignmentEditView):
    template_name = 'projects/sequence_assignment_edit.html'


class SequenceEditView(LoggedInCourseMixin, ProjectReadableMixin,
                       TemplateView):

    template_name = 'projects/sequence.html'

    def get(self, request, *args, **kwargs):
        project = get_object_or_404(Project, pk=kwargs.get('project_id', None))

        data = {
            'project': project,
            'can_edit': request.user == project.author,
            'allow_public_compositions': allow_public_compositions(
                self.request.course)
        }

        return self.render_to_response(data)


class ProjectDispatchView(LoggedInCourseMixin, ProjectReadableMixin, View):

    def dispatch(self, request, *args, **kwargs):
        project = get_object_or_404(Project, pk=kwargs.get('project_id', None))
        parent = project.assignment()
        if (project.is_selection_assignment() or
                (parent and parent.is_selection_assignment())):
            view = SelectionAssignmentView.as_view()
        elif (project.is_sequence_assignment() or
                (parent and parent.is_sequence_assignment())):
            view = SequenceAssignmentView.as_view()
        elif (project.is_sequence()):
            view = SequenceEditView.as_view()
        else:
            # Composition view
            view = DefaultProjectView.as_view()

        return view(request, *args, **kwargs)


class SelectionAssignmentView(AssignmentView):
    template_name = 'projects/selection_assignment_view.html'

    def get_extra_context(self):
        parent = self.get_assignment(self.project)

        item = parent.assignmentitem_set.first().asset
        item_ctx = AssetResource().render_one_context(self.request, item)

        return {
            'item': item,
            'item_json': json.dumps(item_ctx)
        }


class SequenceAssignmentView(AssignmentView):
    template_name = 'projects/sequence_assignment_view.html'

    def get_extra_context(self):
        parent = self.get_assignment(self.project)
        key = 'assignment_instructions_{}'.format(parent.id)
        return {
            'show_instructions': UserSetting.get_setting(
                self.request.user, key, True),
            'allow_public_compositions': allow_public_compositions(
                self.request.course)
        }


class DefaultProjectView(LoggedInCourseMixin, ProjectReadableMixin,
                         JSONResponseMixin, TemplateView):
    """Displays the Composition project view."""

    def get(self, request, *args, **kwargs):
        """
        A multi-panel editable view for the specified project
        Legacy note: Ideally, this function would be named project_view but
        StructuredCollaboration requires the view name
        to be  <class>-view to do a reverse lookup

        Panel 1: Parent Assignment (if applicable)
        Panel 2: Project
        Panel 3: Instructor Feedback (if applicable & exists)

        Keyword arguments:
        project_id -- the model id
        """
        project = get_object_or_404(Project, pk=kwargs.get('project_id', None))
        show_feedback = kwargs.get('feedback', None) == "feedback"
        data = {'space_owner': request.user.username,
                'show_feedback': show_feedback}

        if not request.is_ajax():
            self.template_name = 'projects/project.html'
            data['project'] = project
            return self.render_to_response(data)
        else:
            panels = []

            lst = Vocabulary.objects.filter(course=request.course)
            lst = lst.prefetch_related('term_set')
            vocabulary = VocabularyResource().render_list(request, lst)

            owners = UserResource().render_list(request,
                                                request.course.members)

            is_faculty = request.course.is_faculty(request.user)
            can_edit = project.can_edit(request.course, request.user)
            feedback_discussion = project.feedback_discussion() \
                if is_faculty or can_edit else None

            # Project Parent (assignment) if exists
            parent = project.assignment()
            if parent:
                pedit = parent.can_edit(request.course, request.user)
                resource = ProjectResource(
                    record_viewer=request.user, is_viewer_faculty=is_faculty,
                    editable=pedit)
                ctx = resource.render_one(request, parent)
                state = "open" if (project.is_empty()) else "closed"

                panel = {'is_faculty': is_faculty,
                         'panel_state': state,
                         'subpanel_state': 'closed',
                         'context': ctx,
                         'owners': owners,
                         'vocabulary': vocabulary,
                         'template': 'project'}
                panels.append(panel)

            # Requested project, can be either an assignment or composition
            resource = ProjectResource(record_viewer=request.user,
                                       is_viewer_faculty=is_faculty,
                                       editable=can_edit)
            project_context = resource.render_one(request, project)

            # only editing if it's new
            project_context['editing'] = \
                True if can_edit and len(project.body) < 1 else False

            project_context['create_instructor_feedback'] = \
                is_faculty and parent and not feedback_discussion

            panel = {'is_faculty': is_faculty,
                     'panel_state': 'closed' if show_feedback else 'open',
                     'context': project_context,
                     'template': 'project',
                     'owners': owners,
                     'vocabulary': vocabulary}
            panels.append(panel)

            # Project Response -- if the requested project is an assignment
            # This is primarily a student view. The student's response should
            # pop up automatically when the parent assignment is viewed.
            if project.is_essay_assignment():
                responses = project.responses(request.course,
                                              request.user, request.user)
                if len(responses) > 0:
                    response = responses[0]
                    response_can_edit = response.can_edit(request.course,
                                                          request.user)
                    resource = ProjectResource(record_viewer=request.user,
                                               is_viewer_faculty=is_faculty,
                                               editable=response_can_edit)
                    response_context = resource.render_one(request, response)

                    panel = {'is_faculty': is_faculty,
                             'panel_state': 'closed',
                             'context': response_context,
                             'template': 'project',
                             'owners': owners,
                             'vocabulary': vocabulary}
                    panels.append(panel)

                    if not feedback_discussion and response_can_edit:
                        feedback_discussion = response.feedback_discussion()

            data['panels'] = panels

            # If feedback exists for the requested project
            if feedback_discussion:
                # 3rd pane is the instructor feedback, if it exists
                panel = {'panel_state': 'open' if show_feedback else 'closed',
                         'panel_state_label': "Instructor Feedback",
                         'template': 'discussion',
                         'owners': owners,
                         'vocabulary': vocabulary,
                         'context': threaded_comment_json(request,
                                                          feedback_discussion)}
                panels.append(panel)

            # Create a place for asset editing
            panel = {'panel_state': 'closed',
                     'panel_state_label': "Item Details",
                     'template': 'asset_quick_edit',
                     'update_history': False,
                     'owners': owners,
                     'vocabulary': vocabulary,
                     'context': {'type': 'asset'}}
            panels.append(panel)

            return self.render_to_json_response(data)


@login_required
@allow_http("GET")
def project_export_html(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if not project.can_read(request.course, request.user):
        return HttpResponseForbidden("forbidden")

    template = loader.get_template("projects/export.html")

    context = RequestContext(request, {
        'space_owner': request.user.username,
        'project': project,
        'body': project.body})

    return HttpResponse(template.render(context))


@login_required
@allow_http("GET")
def project_export_msword(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if not project.can_read(request.course, request.user):
        return HttpResponseForbidden("forbidden")

    template = loader.get_template("projects/msword.html")

    body = SherdNote.objects.fully_qualify_references(project.body,
                                                      request.get_host())
    body = body.replace("padding-left", "margin-left")

    context = RequestContext(request, {
        'space_owner': request.user.username,
        'project': project,
        'body': body})

    response = HttpResponse(template.render(context),
                            content_type='application/vnd.ms-word')
    response['Content-Disposition'] = \
        'attachment; filename=%s.doc' % (slugify(project.title))
    return response


class ProjectDetailView(LoggedInCourseMixin, RestrictedMaterialsMixin,
                        AjaxRequiredMixin, JSONResponseMixin,
                        ProjectReadableMixin, View):

    def get(self, request, project_id):
        project = get_object_or_404(Project, id=project_id)

        can_edit = project.can_edit(request.course, request.user)

        resource = ProjectResource(record_viewer=request.user,
                                   is_viewer_faculty=self.is_viewer_faculty,
                                   editable=can_edit)
        context = resource.render_one(request, project)
        return self.render_to_json_response(context)


class ProjectCollectionView(LoggedInCourseMixin, RestrictedMaterialsMixin,
                            AjaxRequiredMixin, JSONResponseMixin, View):

    limit = 10

    def paginate(self, pres, assignments, projects):
        ctx = {'assignments': [], 'projects': []}

        # paginate
        paginator = Paginator(assignments + projects, self.limit)
        page_number = self.request.GET.get('page', 1)
        the_page = paginator.page(page_number)
        if paginator.num_pages > 1:
            ctx['num_pages'] = paginator.num_pages
            ctx['current_page'] = page_number

            if the_page.has_previous():
                ctx['previous_page'] = the_page.previous_page_number()
            if the_page.has_next():
                ctx['next_page'] = the_page.next_page_number()

        for o in the_page.object_list:
            if o in assignments:
                ctx['assignments'].append(
                    pres.render_assignment(self.request, o))
            else:
                ctx['projects'].append(pres.render_project(self.request, o))

        return ctx

    """
    An ajax-only request to retrieve assets for a course or a specified user
    Example:
        /api/project/user/sld2131/
        /api/project/
    """
    def get(self, request):
        ures = UserResource()
        course_res = CourseResource()
        pres = ProjectResource(editable=self.viewing_own_records,
                               record_viewer=self.record_viewer,
                               is_viewer_faculty=self.is_viewer_faculty)
        assignments = []

        ctx = {
            'space_viewer': ures.render_one(request, self.record_viewer),
            'editable': self.viewing_own_records,
            'course': course_res.render_one(request, request.course),
            'is_faculty': self.is_viewer_faculty,
            'is_superuser': request.user.is_superuser,
        }

        if self.record_owner:
            ctx['space_owner'] = ures.render_one(request, self.record_owner)

            if not request.course.is_true_member(self.record_owner):
                return self.render_to_json_response(ctx)

            projects = Project.objects.visible_by_course_and_user(
                request.course, request.user, self.record_owner,
                self.viewing_faculty_records)

            # Show unresponded assignments if viewing self & self is a student
            if not self.is_viewer_faculty and self.viewing_own_records:
                assignments = Project.objects.unresponded_assignments(
                    request.course, request.user)
        else:
            projects = Project.objects.visible_by_course(request.course,
                                                         request.user)

        # update counts and paginate
        ctx['compositions'] = len(projects) > 0 or len(assignments) > 0
        ctx.update(self.paginate(pres, assignments, projects))
        return self.render_to_json_response(ctx)


class ProjectSortView(LoggedInFacultyMixin, AjaxRequiredMixin,
                      JSONResponseMixin, CreateReversionMixin, View):
    '''
    An ajax-only request to update project ordinality. Used by instructors
    to tune the "From Your Instructor" list on the homepage
    '''
    def post(self, request):
        ids = request.POST.getlist("project")
        for idx, project_id in enumerate(ids):
            project = Project.objects.get(id=project_id)
            if idx != project.ordinality:
                project.ordinality = idx
                project.save()

        return self.render_to_json_response({'sorted': 'true'})


class ProjectItemView(LoggedInCourseMixin, JSONResponseMixin,
                      AjaxRequiredMixin, View):

    def get(self, *args, **kwargs):
        item = get_object_or_404(Asset, id=kwargs.get('asset_id', None))

        parent = get_object_or_404(Project, id=kwargs.get('project_id', None))

        responses = parent.responses(self.request.course, self.request.user)
        response_ids = [r.id for r in responses]

        # notes related to visible responses are visible
        pnotes = ProjectNote.objects.filter(project__id__in=response_ids)
        note_ids = pnotes.values_list('annotation__id', flat=True)
        notes = SherdNote.objects.filter(id__in=note_ids)

        if item.primary.is_image():
            notes = notes.order_by('author', 'title')
        else:
            notes = notes.order_by('author', 'range1', 'title')

        notes = notes.prefetch_related('author', 'asset')

        ctx = AssetResource().render_one_context(self.request, item, notes)

        return self.render_to_json_response(ctx)
