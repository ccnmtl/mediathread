from django import forms
from django.db import models
from django.contrib.admin import widgets
from projects.models import *
from courseaffils.lib import get_public_name
from mediathread_main import course_details

class ProjectForm(forms.ModelForm):

    submit = forms.ChoiceField(choices=(('Preview','Preview'),
                                        ('Save','Save'),
                                        ))

    publish = forms.ChoiceField(choices=PUBLISH_OPTIONS,#from models
                                label='Status:',
                                )

    parent =  forms.CharField(required=False,label='Response to',
                              #choices=[(1,1)],
                              )
    class Meta:
        model = Project
        fields = ('title','body','participants','submit','publish')

    def __init__(self,request, *args, **kwargs):
        super(ProjectForm,self).__init__(*args,**kwargs)
        self.fields['participants'].widget = widgets.FilteredSelectMultiple("participants",False) 
        
        lst = [(u.id,get_public_name(u, request)) for u in request.course.user_set.all()]
        self.fields['participants'].choices = sorted(lst, key=lambda participant: participant[1])   # sort by name
        
        
        col = kwargs['instance'].collaboration()
        if col:
            pol = col._policy.policy_name
            if pol not in dict(self.fields['publish'].choices):
                self.fields['publish'].choices.append( (pol,pol) )
            self.initial['publish'] = pol
        
        if not request.course.is_faculty(request.user):
            self.fields['publish'].choices = [choice for choice in self.fields['publish'].choices
                                              if choice[0] not in PUBLISH_OPTIONS_FACULTY_ONLY]

        if not course_details.allow_public_compositions(request.course):
            self.fields['publish'].choices = [choice for choice in self.fields['publish'].choices
                                              if choice[0] not in PUBLISH_OPTIONS_PUBLIC]
            
        
        #not restrictive enough -- people can add children to their own projects
        # is that a good idea?
        # necessary to add a discussion to it, but maybe that's a workaround
        # how about we just have people 'create' a project from the assignment page for now.
        #self.fields['parent'].choices = [(sc.id,sc.title) for sc in 
        #                                 Collaboration.objects.filter(context=request.collaboration_context,
        #                                                              content_type = ContentType.objects.get_for_model(Project))
        #                                 if sc.permission_to('add_child',request)
        #                                 ]
            

        self.fields['participants'].required = False
        self.fields['body'].required = False
        self.fields['submit'].required = False
        self.fields['publish'].required = False
        self.fields['title'].widget.attrs['maxlength'] = 80 #for structured collaboration
