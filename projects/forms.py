from courseaffils.lib import get_public_name
from django import forms
from django.forms.widgets import RadioSelect
from mediathread_main import course_details
from projects.models import Project, PUBLISH_OPTIONS, PUBLISH_OPTIONS_FACULTY
from projects.models import PUBLISH_OPTIONS_STUDENT_ASSIGNMENT
from projects.models import PUBLISH_OPTIONS_STUDENT_COMPOSITION
from projects.models import PUBLISH_OPTIONS_PUBLIC


class ProjectForm(forms.ModelForm):

    submit = forms.ChoiceField(choices=(('Preview', 'Preview'),
                                        ('Save', 'Save'),))

    publish = forms.ChoiceField(choices=PUBLISH_OPTIONS,  # from models
                                label='Visibility',
                                widget=RadioSelect)

    parent = forms.CharField(required=False, label='Response to',)

    class Meta:
        model = Project
        fields = ('title', 'body', 'participants',
                  'submit', 'publish', 'due_date')

    def __init__(self, request, *args, **kwargs):
        super(ProjectForm, self).__init__(*args, **kwargs)

        lst = [(u.id, get_public_name(u, request))
               for u in request.course.user_set.all()]
        self.fields['participants'].choices = sorted(
            lst, key=lambda participant: participant[1])
        self.fields['participants'].widget.attrs = {
            'id': "id_participants_%s" % self.instance.id
        }

        col = kwargs['instance'].collaboration()
        if col:
            pol = col._policy.policy_name
            if pol not in dict(self.fields['publish'].choices):
                self.fields['publish'].choices.append((pol, pol))
            self.initial['publish'] = pol

        if request.course.is_faculty(request.user):
            # Faculty
            self.fields['publish'].choices = \
                [choice for choice in self.fields['publish'].choices
                 if choice[0] in PUBLISH_OPTIONS_FACULTY]
        else:
            # Student
            if kwargs['instance'].assignment():
                # Assignment response
                self.fields['publish'].choices = \
                    [choice for choice in self.fields['publish'].choices
                     if choice[0] in PUBLISH_OPTIONS_STUDENT_ASSIGNMENT]
            else:
                self.fields['publish'].choices = \
                    [choice for choice in self.fields['publish'].choices
                     if choice[0] in PUBLISH_OPTIONS_STUDENT_COMPOSITION]

        if course_details.allow_public_compositions(request.course):
            self.fields['publish'].choices.append(PUBLISH_OPTIONS_PUBLIC)

        self.fields['participants'].required = False
        self.fields['body'].required = False
        self.fields['submit'].required = False
        self.fields['publish'].required = False

        # for structured collaboration
        self.fields['title'].widget.attrs['maxlength'] = 80
