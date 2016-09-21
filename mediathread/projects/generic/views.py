import json

from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404
from django.views.generic.base import TemplateView

from mediathread.assetmgr.api import AssetResource
from mediathread.mixins import LoggedInCourseMixin, ProjectReadableMixin, \
    LoggedInFacultyMixin
from mediathread.projects.forms import ProjectForm
from mediathread.projects.models import Project, RESPONSE_VIEW_POLICY, \
    PUBLISH_WHOLE_CLASS
from mediathread.taxonomy.api import VocabularyResource
from mediathread.taxonomy.models import Vocabulary


class AssignmentView(LoggedInCourseMixin, ProjectReadableMixin, TemplateView):
    extra_context = dict()

    def get_extra_context(self):
        return self.extra_context

    def get_assignment(self, project):
        if project.is_assignment_type():
            assignment = project
        else:
            assignment = project.assignment()
        return assignment

    def get_my_response(self, responses):
        for response in responses:
            if response.is_participant(self.request.user):
                return response
        return None

    def get_feedback(self, responses, is_faculty):
        ctx = {}
        existing = 0
        for response in responses:
            ctx[response.author.username] = {'responseId': response.id}

            feedback = response.feedback_discussion()
            if feedback and (is_faculty or
                             response.is_participant(self.request.user)):
                existing += 1
                ctx[response.author.username]['comment'] = {
                    'id': feedback.id,
                    'content': feedback.comment
                }
        return ctx, existing

    def get_context_data(self, **kwargs):
        project = get_object_or_404(Project, pk=kwargs.get('project_id', None))
        parent = self.get_assignment(project)
        can_edit = parent.can_edit(self.request.course, self.request.user)
        responses = parent.responses(self.request.course, self.request.user)
        my_response = self.get_my_response(responses)
        is_faculty = self.request.course.is_faculty(self.request.user)

        item = parent.assignmentitem_set.first().asset
        item_ctx = AssetResource().render_one_context(self.request, item)

        lst = Vocabulary.objects.filter(course=self.request.course)
        lst = lst.prefetch_related('term_set')
        vocabulary_json = VocabularyResource().render_list(
            self.request, lst)

        feedback, feedback_count = self.get_feedback(responses, is_faculty)

        ctx = {
            'is_faculty': is_faculty,
            'assignment': parent,
            'assignment_can_edit': can_edit,
            'item': item,
            'item_json': json.dumps(item_ctx),
            'my_response': my_response,
            'response_view_policies': RESPONSE_VIEW_POLICY,
            'submit_policy': PUBLISH_WHOLE_CLASS[0],
            'vocabulary': json.dumps(vocabulary_json),
            'responses': responses,
            'feedback': json.dumps(feedback),
            'feedback_count': feedback_count
        }
        ctx.update(self.get_extra_context())
        return ctx


class AssignmentEditView(LoggedInFacultyMixin, TemplateView):

    def get(self, *args, **kwargs):
        try:
            project = Project.objects.get(id=kwargs.get('project_id', None))
            if (not project.can_edit(self.request.course, self.request.user)):
                return HttpResponseForbidden("forbidden")
            form = ProjectForm(self.request, instance=project)
        except Project.DoesNotExist:
            form = ProjectForm(self.request, instance=None)

        return self.render_to_response({
            'form': form
        })
