import json

from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404
from django.views.generic.base import TemplateView

from mediathread.mixins import LoggedInCourseMixin, ProjectReadableMixin, \
    LoggedInFacultyMixin
from mediathread.projects.forms import ProjectForm
from mediathread.projects.models import Project, RESPONSE_VIEW_POLICY, \
    PUBLISH_WHOLE_CLASS
from mediathread.taxonomy.api import VocabularyResource
from mediathread.taxonomy.models import Vocabulary


class AssignmentView(LoggedInCourseMixin, ProjectReadableMixin, TemplateView):

    def get_extra_context(self):
        return dict()

    def get_assignment(self, project):
        if project.is_assignment_type():
            return project
        else:
            return project.assignment()

    def get_my_response(self, responses):
        for response in responses:
            if response.is_participant(self.request.user):
                return response
        return None

    def get_peer_response(self, project):
        if not project.is_assignment_type():
            return project

        return None

    def response_can_edit(self, the_response):
        return (the_response is not None and
                the_response.author == self.request.user)

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
        # passed project may identify the assignment or a response
        project = get_object_or_404(Project, pk=kwargs.get('project_id', None))
        parent = self.get_assignment(project)
        assignment_can_edit = \
            parent.can_edit(self.request.course, self.request.user)

        responses = parent.responses(self.request.course, self.request.user)

        peer_response = self.get_peer_response(project)
        my_response = self.get_my_response(responses)
        the_response = peer_response or my_response
        response_can_edit = self.response_can_edit(the_response)

        lst = Vocabulary.objects.filter(course=self.request.course)
        lst = lst.prefetch_related('term_set')
        vocabulary_json = VocabularyResource().render_list(
            self.request, lst)

        is_faculty = self.request.course.is_faculty(self.request.user)
        feedback, feedback_count = self.get_feedback(responses, is_faculty)

        students = self.request.course.students.order_by(
            'last_name', 'first_name', 'username')

        self.ctx = {
            'is_faculty': is_faculty,
            'assignment': parent,
            'assignment_can_edit': assignment_can_edit,
            'my_response': my_response,
            'the_response': the_response,
            'response_can_edit': response_can_edit,
            'response_view_policies': RESPONSE_VIEW_POLICY,
            'submit_policy': PUBLISH_WHOLE_CLASS[0],
            'vocabulary': json.dumps(vocabulary_json),
            'responses': responses,
            'feedback': json.dumps(feedback),
            'feedback_count': feedback_count,
            'students': students
        }
        self.ctx.update(self.get_extra_context())
        return self.ctx


class AssignmentEditView(LoggedInFacultyMixin, TemplateView):

    def get_extra_context(self):
        return dict()

    def get_context_data(self, **kwargs):
        try:
            project = Project.objects.get(id=kwargs.get('project_id', None))
            if (not project.can_edit(self.request.course, self.request.user)):
                return HttpResponseForbidden("forbidden")
            form = ProjectForm(self.request, instance=project)
        except Project.DoesNotExist:
            form = ProjectForm(self.request, instance=None)

        ctx = {'form': form}
        ctx.update(self.get_extra_context())
        return ctx
