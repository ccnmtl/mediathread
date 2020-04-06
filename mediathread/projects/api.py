# pylint: disable-msg=R0904
from random import choice

from string import ascii_letters

from courseaffils.lib import get_public_name

from django.urls import reverse
from django.utils.encoding import smart_text

from tastypie import fields
from tastypie.resources import ModelResource

from mediathread.api import UserResource, ClassLevelAuthentication
from mediathread.assetmgr.api import AssetResource
from mediathread.djangosherd.api import SherdNoteResource
from mediathread.projects.forms import ProjectForm
from mediathread.projects.models import Project


class ProjectResource(ModelResource):

    author = fields.ForeignKey(UserResource, 'author', full=True)

    date_fmt = "%m/%d/%y %I:%M %p"

    def __init__(self, *args, **kwargs):
        # @todo: extras is a side-effect of the Mustache templating system
        # not supporting the ability to reference variables in the parent
        # context. ideally, the templating system should be switched out to
        # something more reasonable
        self.editable = kwargs.pop('editable', {})
        self.record_viewer = kwargs.pop('record_viewer', {})
        self.is_viewer_faculty = kwargs.pop('is_viewer_faculty', False)
        self.extras = kwargs.pop('extras', {})
        super(ProjectResource, self).__init__(*args, **kwargs)

    class Meta:
        queryset = Project.objects.all().order_by('id')
        excludes = ['participants', 'body',
                    'feedback', 'sherdnote_set']
        list_allowed_methods = []
        detail_allowed_methods = []
        authentication = ClassLevelAuthentication()
        ordering = ['id', 'title']

    def dehydrate(self, bundle):
        bundle.data['is_essay_assignment'] = bundle.obj.is_essay_assignment()
        bundle.data['is_selection_assignment'] = \
            bundle.obj.is_selection_assignment()
        bundle.data['is_sequence_assignment'] = \
            bundle.obj.is_sequence_assignment()
        bundle.data['is_sequence'] = bundle.obj.is_sequence()
        bundle.data['description'] = bundle.obj.description()
        bundle.data['is_response'] = bundle.obj.assignment() is not None
        bundle.data['attribution'] = bundle.obj.attribution()

        if hasattr(self, 'request') and hasattr(self.request, 'course') \
           and self.request.course:
            bundle.data['url'] = reverse('project-workspace', kwargs={
                'course_pk': self.request.course.pk,
                'project_id': bundle.obj.pk,
            })
        else:
            bundle.data['url'] = bundle.obj.get_absolute_url()

        bundle.data['due_date'] = bundle.obj.get_due_date()
        bundle.data['modified_date'] = bundle.obj.modified.strftime("%m/%d/%y")
        bundle.data['modified_time'] = bundle.obj.modified.strftime("%I:%M %p")
        bundle.data['editable'] = self.editable
        bundle.data['is_faculty'] = self.is_viewer_faculty
        bundle.data['submitted'] = bundle.obj.is_submitted()

        participants = bundle.obj.attribution_list()
        bundle.data['participants'] = [{
            'name': p.get_full_name(),
            'username': p.username,
            'public_name': get_public_name(p, bundle.request),
            'is_viewer': self.record_viewer == p.username,
            'last': idx == (len(participants) - 1)
        } for idx, p in enumerate(participants)]
        bundle.data['status'] = bundle.obj.status()

        for key, value in self.extras.items():
            bundle.data[key] = value

        return bundle

    def all_responses(self, request, project):
        ctx = []
        responses = project.responses(request.course, request.user)

        for response in responses:
            submitted = ''
            if response.is_submitted():
                submitted = response.date_submitted.strftime(self.date_fmt)

            obj = {
                'url': response.get_absolute_url(),
                'title': response.title,
                'submitted': submitted,
                'modified': response.modified.strftime(self.date_fmt),
                'attribution_list': []}

            last = len(response.attribution_list()) - 1
            for idx, author in enumerate(response.attribution_list()):
                obj['attribution_list'].append({
                    'name': get_public_name(author, request),
                    'last': idx == last})

            ctx.append(obj)

        return sorted(
            ctx,
            key=lambda response: response['attribution_list'][0]['name'])

    def my_responses(self, request, project):
        ctx = []
        responses = project.responses(request.course,
                                      request.user, request.user)
        for response in responses:
            obj = {'url': response.get_absolute_url(),
                   'title': response.title,
                   'modified': response.modified.strftime(self.date_fmt),
                   'attribution_list': []}

            last = len(response.attribution_list()) - 1
            for idx, author in enumerate(response.attribution_list()):
                obj['attribution_list'].append({
                    'name': get_public_name(author, request),
                    'last': idx == last})

            ctx.append(obj)

        return ctx

    def related_assets_notes(self, request, project):

        asset_resource = AssetResource()
        sherd_resource = SherdNoteResource()

        rand = ''.join([choice(ascii_letters) for i in range(5)])  # nosec

        assets = {}
        notes = []
        for note in project.citations():
            notes.append(sherd_resource.render_one(request, note, rand))
            if (note.title not in ["Annotation Deleted", 'Asset Deleted']):
                key = '%s_%s' % (rand, note.asset.pk)
                if key not in assets.keys():
                    assets[key] = \
                        asset_resource.render_one(request, note.asset)

        return assets, notes

    def render_one(self, request, project, version_number=None):
        self.request = request
        bundle = self.build_bundle(obj=project, request=request)
        dehydrated = self.full_dehydrate(bundle)
        project_ctx = self._meta.serializer.to_simple(dehydrated, None)
        project_ctx['body'] = project.body
        project_ctx['public_url'] = project.public_url()
        project_ctx['modified'] = project.modified.strftime(self.date_fmt)
        project_ctx['current_version'] = version_number
        project_ctx['visibility'] = project.visibility_short()
        project_ctx['visibility_long'] = project.visibility()
        project_ctx['type'] = project.project_type

        assets, notes = self.related_assets_notes(request, project)

        data = {
            'project': project_ctx,
            'type': 'project',
            'can_edit': self.editable,
            'annotations': notes,
            'assets': assets
        }

        data['responses'] = self.all_responses(request, project)
        data['response_count'] = len(data['responses'])

        my_responses = self.my_responses(request, project)
        if len(my_responses) == 1:
            data['my_response'] = my_responses[0]
        elif len(my_responses) > 1:
            data['my_responses'] = my_responses
            data['my_responses_count'] = len(my_responses)

        if self.editable:
            projectform = ProjectForm(request, instance=project)
            data['form'] = {
                'participants': smart_text(projectform['participants']),
                'publish': smart_text(projectform['publish']),
                'response_view_policy': smart_text(
                    projectform['response_view_policy']),
            }

        return data

    def render_assignment(self, request, assignment):
        bundle = self.build_bundle(obj=assignment, request=request)
        dehydrated = self.full_dehydrate(bundle)
        ctx = self._meta.serializer.to_simple(dehydrated, None)
        ctx['display_as_assignment'] = True
        return ctx

    def render_project(self, request, project):
        self.request = request
        course = request.course
        user = request.user

        abundle = self.build_bundle(obj=project, request=request)
        dehydrated = self.full_dehydrate(abundle)
        ctx = self._meta.serializer.to_simple(dehydrated, None)

        if project.is_assignment_type():
            responses = project.responses(course, user)
            ctx['responses'] = len(responses)
            ctx['is_assignment_type'] = True
            ctx['display_as_assignment'] = True
        else:
            parent_assignment = project.assignment()
            if parent_assignment:
                if self.editable:
                    feedback = project.feedback_discussion()
                    if feedback:
                        ctx['feedback'] = feedback.id
                ctx['display_as_assignment'] = True
                ctx['collaboration'] = {}
                ctx['collaboration']['title'] = parent_assignment.title
                ctx['collaboration']['url'] = \
                    parent_assignment.get_absolute_url()
                ctx['collaboration']['due_date'] = \
                    parent_assignment.get_due_date()

        return ctx

    def render_list(self, request, projects):
        self.request = request
        lst = []
        for project in projects.all():
            bundle = self.build_bundle(obj=project, request=request)
            dehydrated = self.full_dehydrate(bundle)
            ctx = self._meta.serializer.to_simple(dehydrated, None)
            lst.append(ctx)
        return sorted(lst, key=lambda item: item['title'])
