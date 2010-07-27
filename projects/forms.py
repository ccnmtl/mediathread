from django import forms
from django.db import models

from projects.models import *

class ProjectForm(forms.ModelForm):

    submit = forms.ChoiceField(choices=(('Preview','Preview'),
                                        ('Save','Save'),
                                        ))

    publish = forms.ChoiceField(choices=(('PrivateEditorsAreOwners','Draft (only collaborators)'),
                                         ('PrivateStudentAndFaculty','Instructor Only'),
                                         ('CourseProtected','Course participants'),
                                         ('PublicEditorsAreOwners','World'),
                                         ),
                                label='Share with',
                                )
    class Meta:
        model = Project
        fields = ('title','body','participants','submit','publish')
    
    def __init__(self,request, *args, **kwargs):
        super(ProjectForm,self).__init__(*args,**kwargs)
        self.fields['participants'].choices = [(u.id,u.get_full_name() or u.username) for u in request.course.user_set.all()]
        col = kwargs['instance'].collaboration()
        if col:
            self.initial['publish'] = col._policy.policy_name

        self.fields['participants'].required = False
        self.fields['body'].required = False
        self.fields['submit'].required = False
        self.fields['publish'].required = False
