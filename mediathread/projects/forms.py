from courseaffils.lib import get_public_name
from django import forms
from django.forms.widgets import RadioSelect

from mediathread.main import course_details
from mediathread.main.course_details import all_selections_are_visible
from mediathread.projects.models import PUBLISH_OPTIONS_PUBLIC, \
    PUBLISH_OPTIONS_STUDENT, PUBLISH_OPTIONS, PUBLISH_OPTIONS_FACULTY, \
    RESPONSE_VIEW_POLICY, RESPONSE_VIEW_NEVER, RESPONSE_VIEW_SUBMITTED, \
    RESPONSE_VIEW_ALWAYS
from mediathread.projects.models import Project


class ProjectForm(forms.ModelForm):

    submit = forms.ChoiceField(choices=(('Preview', 'Preview'),
                                        ('Save', 'Save'),))

    publish = forms.ChoiceField(choices=PUBLISH_OPTIONS,
                                label='Visibility', widget=RadioSelect)

    parent = forms.CharField(required=False, label='Response to',)

    response_view_policy = forms.ChoiceField(choices=RESPONSE_VIEW_POLICY,
                                             widget=RadioSelect)

    class Meta:
        model = Project
        fields = ('title', 'body', 'participants',
                  'submit', 'publish', 'due_date',
                  'response_view_policy')

    def __init__(self, request, *args, **kwargs):
        super(ProjectForm, self).__init__(*args, **kwargs)

        lst = [(u.id, get_public_name(u, request))
               for u in request.course.user_set.all()]
        self.fields['participants'].choices = sorted(
            lst, key=lambda participant: participant[1])
        self.fields['participants'].widget.attrs = {
            'id': "id_participants_%s" % self.instance.id
        }

        if kwargs['instance']:
            col = kwargs['instance'].get_collaboration()
            if col:
                pol = col.policy_record.policy_name
                if pol not in dict(self.fields['publish'].choices):
                    self.fields['publish'].choices.append((pol, pol))
                self.initial['publish'] = pol
        else:
            self.instance = None

        if request.course.is_faculty(request.user):
            # Faculty
            self.fields['publish'].choices = \
                [choice for choice in self.fields['publish'].choices
                 if choice[0] in PUBLISH_OPTIONS_FACULTY]
        else:
            # Student
            self.fields['publish'].choices = \
                [choice for choice in self.fields['publish'].choices
                 if choice[0] in PUBLISH_OPTIONS_STUDENT]

        if course_details.allow_public_compositions(request.course):
            if not kwargs['instance'] or kwargs['instance'].is_composition():
                self.fields['publish'].choices.append(PUBLISH_OPTIONS_PUBLIC)

        choices = [RESPONSE_VIEW_NEVER]
        if all_selections_are_visible(request.course):
            choices.append(RESPONSE_VIEW_SUBMITTED)
            choices.append(RESPONSE_VIEW_ALWAYS)
        self.fields['response_view_policy'].choices = choices

        self.fields['participants'].required = False
        self.fields['body'].required = False
        self.fields['submit'].required = False
        self.fields['publish'].required = False
        self.fields['response_view_policy'].required = False

        # for structured collaboration
        self.fields['title'].widget.attrs['maxlength'] = 80
