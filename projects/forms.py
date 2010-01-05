from django import forms
from django.db import models

from projects.models import *

class ProjectForm(forms.ModelForm):

    submit = forms.ChoiceField(choices=(('Save draft','Save draft'),
                                      ('Preview','Preview'),
                                      ('Submit','Submit'),
                                      ))
    class Meta:
        model = Project
        fields = ('title','body','participants','submit')
    
    def __init__(self,request, *args, **kwargs):
        super(ProjectForm,self).__init__(*args,**kwargs)
        self.fields['participants'].queryset = request.course.user_set.get_query_set()
        self.fields['participants'].required = False
        self.fields['body'].required = False
        self.fields['submit'].required = False
