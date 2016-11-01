from courseaffils.lib import get_public_name
from django import forms
from django.forms.widgets import RadioSelect

from mediathread.main import course_details
from mediathread.main.course_details import all_selections_are_visible
from mediathread.projects.models import Project, PUBLISH_WHOLE_WORLD, \
    PUBLISH_OPTIONS
from mediathread.projects.models import \
    RESPONSE_VIEW_POLICY, RESPONSE_VIEW_NEVER, RESPONSE_VIEW_SUBMITTED, \
    RESPONSE_VIEW_ALWAYS, PUBLISH_DRAFT, PUBLISH_WHOLE_CLASS, \
    PUBLISH_INSTRUCTOR_SHARED


class ProjectForm(forms.ModelForm):

    submit = forms.ChoiceField(choices=(('Preview', 'Preview'),
                                        ('Save', 'Save'),))

    publish = forms.ChoiceField(choices=PUBLISH_OPTIONS,
                                label='Visibility', widget=RadioSelect)

    parent = forms.CharField(required=False, label='Response to',)

    response_view_policy = forms.ChoiceField(choices=RESPONSE_VIEW_POLICY,
                                             widget=RadioSelect,
                                             required=False)

    class Meta:
        model = Project
        fields = ('title', 'body', 'participants',
                  'submit', 'publish', 'due_date',
                  'response_view_policy',
                  'custom_instructions_1', 'custom_instructions_2')

    def __init__(self, request, *args, **kwargs):
        super(ProjectForm, self).__init__(*args, **kwargs)

        lst = [(u.id, get_public_name(u, request))
               for u in request.course.user_set.all()]
        self.fields['participants'].choices = sorted(
            lst, key=lambda participant: participant[1])
        self.fields['participants'].widget.attrs = {
            'id': "id_participants_%s" % self.instance.id
        }

        project = kwargs['instance']
        if project:
            # set initial publish value
            col = project.get_collaboration()
            if col:
                self.initial['publish'] = col.policy_record.policy_name
        else:
            self.instance = None

        choices = self.get_choices(request, project)
        self.fields['publish'].choices = choices

        # response view policy. limit choices if there is no project
        # or the project is a selection assignment
        if (not project or not project.is_composition()):
            choices = [RESPONSE_VIEW_NEVER]
            if all_selections_are_visible(request.course):
                choices.append(RESPONSE_VIEW_SUBMITTED)
                choices.append(RESPONSE_VIEW_ALWAYS)
            self.fields['response_view_policy'].choices = choices

        self.fields['participants'].required = False
        self.fields['body'].required = False
        self.fields['submit'].required = False
        self.fields['publish'].required = False

        # for structured collaboration
        self.fields['title'].widget.attrs['maxlength'] = 80

    def get_choices(self, request, project):
        choices = []
        if request.course.is_faculty(request.user):
            if not project or project.get_collaboration().children.count() < 1:
                choices.append(PUBLISH_DRAFT)
            choices.append(PUBLISH_WHOLE_CLASS)
        else:
            # Student
            choices.append(PUBLISH_DRAFT)
            choices.append(PUBLISH_INSTRUCTOR_SHARED)
            choices.append(PUBLISH_WHOLE_CLASS)

        if course_details.allow_public_compositions(request.course):
            if project and project.is_composition():
                choices.append(PUBLISH_WHOLE_WORLD)

        return choices
