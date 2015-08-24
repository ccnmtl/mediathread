# pylint: disable-msg=R0904
from courseaffils.lib import get_public_name
from mediathread.api import UserResource, ClassLevelAuthentication
from mediathread.assetmgr.api import AssetResource
from mediathread.djangosherd.api import SherdNoteResource
from mediathread.projects.forms import ProjectForm
from mediathread.projects.models import Project
from random import choice
from string import letters
from tastypie import fields
from tastypie.resources import ModelResource


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
        bundle.data['is_assignment'] = bundle.obj.is_assignment()
        bundle.data['is_selection_assignment'] = \
            bundle.obj.is_selection_assignment()
        bundle.data['description'] = bundle.obj.description()
        bundle.data['is_response'] = bundle.obj.assignment() is not None
        bundle.data['attribution'] = bundle.obj.attribution()
        bundle.data['url'] = bundle.obj.get_absolute_url()
        bundle.data['due_date'] = bundle.obj.get_due_date()
        bundle.data['modified_date'] = bundle.obj.modified.strftime("%m/%d/%y")
        bundle.data['modified_time'] = bundle.obj.modified.strftime("%I:%M %p")
        bundle.data['editable'] = self.editable
        bundle.data['is_faculty'] = self.is_viewer_faculty
        bundle.data['submitted'] = bundle.obj.submitted

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
            obj = {
                'url': response.get_absolute_url(),
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

        rand = ''.join([choice(letters) for i in range(5)])

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
        bundle = self.build_bundle(obj=project, request=request)
        dehydrated = self.full_dehydrate(bundle)
        project_ctx = self._meta.serializer.to_simple(dehydrated, None)
        project_ctx['body'] = project.body
        project_ctx['public_url'] = project.public_url()
        project_ctx['current_version'] = version_number
        project_ctx['visibility'] = project.visibility_short()
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

        if project.is_participant(request.user):
            data['revisions'] = [{
                'version_number': v.version_number,
                'versioned_id': v.versioned_id,
                'author': get_public_name(v.instance().author, request),
                'modified': v.modified.strftime("%m/%d/%y %I:%M %p")}
                for v in project.versions.order_by('-change_time')]

        if self.editable:
            projectform = ProjectForm(request, instance=project)
            data['form'] = {
                'participants': projectform['participants'].__unicode__(),
                'publish': projectform['publish'].__unicode__()
            }

        return data

    def render_assignments(self, request, assignments):
        lst = []
        for a in assignments:
            bundle = self.build_bundle(obj=a, request=request)
            dehydrated = self.full_dehydrate(bundle)
            ctx = self._meta.serializer.to_simple(dehydrated, None)
            ctx['display_as_assignment'] = True
            lst.append(ctx)
        return lst

    def render_projects(self, request, projects):
        course = request.course
        user = request.user

        lst = []
        for project in projects:
            abundle = self.build_bundle(obj=project, request=request)
            dehydrated = self.full_dehydrate(abundle)
            ctx = self._meta.serializer.to_simple(dehydrated, None)

            if self.editable:
                feedback = project.feedback_discussion()
                if feedback:
                    ctx['feedback'] = feedback.id

            parent_assignment = project.assignment()
            if parent_assignment:
                ctx['display_as_assignment'] = True
                ctx['collaboration'] = {}
                ctx['collaboration']['title'] = parent_assignment.title
                ctx['collaboration']['url'] = \
                    parent_assignment.get_absolute_url()
                ctx['collaboration']['due_date'] = \
                    parent_assignment.get_due_date()
            elif project.is_assignment() or project.is_selection_assignment():
                responses = project.responses(course, user)
                ctx['responses'] = len(responses)
                ctx['is_assignment'] = True
                ctx['display_as_assignment'] = True

            lst.append(ctx)
        return lst

    def render_list(self, request, projects):
        lst = []
        for project in projects.all():
            bundle = self.build_bundle(obj=project, request=request)
            dehydrated = self.full_dehydrate(bundle)
            ctx = self._meta.serializer.to_simple(dehydrated, None)
            lst.append(ctx)
        return sorted(lst, key=lambda item: item['title'])
