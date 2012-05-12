import simplejson
from random import choice
from string import letters

from django.core.urlresolvers import reverse
from django.db.models import get_model
from django.http import HttpResponseRedirect, HttpResponseForbidden, HttpResponse, Http404
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from djangohelpers.lib import allow_http

from discussions.views import threaded_comment_json
from courseaffils.lib import in_course_or_404, in_course, get_public_name
from projects.forms import ProjectForm

Project = get_model('projects','project')
ProjectVersion = get_model('projects','projectversion')

@allow_http("POST")
def project_create(request):
    if request.method != "POST":
        return HttpResponseForbidden("forbidden")

    user = request.user
    course = request.course 
    in_course_or_404(user, course)
    is_faculty = course.is_faculty(user),
    
    project = Project(author=user, course=course, title="Untitled")
    project.save()

    project.collaboration(request, sync_group=True)

    parent = request.POST.get("parent")
    if parent is not None:
        try:
            parent = Project.objects.get(pk=parent)
            
            parent_collab = parent.collaboration(request)
            if parent_collab.permission_to("add_child", request):
                parent_collab.append_child(project)

        except Project.DoesNotExist:
            parent = None
            # @todo -- an error has occurred

    if not request.is_ajax():
        return HttpResponseRedirect(project.get_absolute_url())
    else: 
        project_context = project_json(request, project, project.can_edit(request))    
        project_context['editing'] = True
        
        data = { 'panel_state': 'open', 
                 'template': 'project',
                 'context': project_context 
        }
                
        return HttpResponse(simplejson.dumps(data, indent=2), mimetype='application/json')

@allow_http("POST")
def project_save(request, project_id):
    project = get_object_or_404(Project, pk=project_id, course=request.course)

    if not project.can_edit(request) or not request.method == "POST":
        return HttpResponseRedirect(project.get_absolute_url())

    space_owner = in_course_or_404(project.author.username, request.course)

    if request.method == "POST":
        projectform = ProjectForm(request, instance=project, data=request.POST)
        if projectform.is_valid():

            #legacy and for optimizing queries
            projectform.instance.submitted = (request.POST.get('publish',None) != 'PrivateEditorsAreOwners')
            
            #this changes for version-tracking purposes
            projectform.instance.author = request.user
            projectform.save()

            projectform.instance.collaboration(request, sync_group=True)

            if request.META.get('HTTP_ACCEPT','').find('json') >=0:
                v_num = projectform.instance.get_latest_version()
                return HttpResponse(simplejson.dumps(
                        {'status':'success',
                         'revision':{
                                'id': v_num,
                                'public_url': projectform.instance.public_url(),
                                'visibility': project.visibility()
                                }
                         }, indent=2),
                                    mimetype='application/json')

        redirect_to = '.'
        return HttpResponseRedirect(redirect_to)
    

@allow_http("POST")
def project_delete(request, project_id):
    """
    Delete the requested project. Regular access conventions apply. 
    If the logged-in user is not allowed to delete the project, an HttpResponseForbidden
    will be returned
    """
    project = get_object_or_404(Project, pk=project_id, course=request.course)
    
    if not project.can_edit(request) or not request.method == "POST":
        return HttpResponseForbidden("forbidden")

    project.delete()
    return HttpResponseRedirect('/')

@allow_http("GET")
def project_view_readonly(request, project_id, version_number=None):
    """
    A single panel read-only view of the specified project/version combination.
    No assignment, response or feedback access/links.
    Regular access conventions apply. For example, if the project is "private"
    an HTTPResponseForbidden will be returned.
    
    Used for reviewing old project versions and public project access.
    
    Keyword arguments:
    project_id -- the model id
    version_number -- a specific project version or None for the current version 
    
    """
    
    project = get_object_or_404(Project, pk = project_id)
    
    if not project.can_read(request):
        return HttpResponseForbidden("forbidden")
    
    if not version_number:
        versions = project.versions.order_by('-change_time')
        version_number = versions[0].version_number
    
    data = { 'space_owner' : request.user.username }
    
    course = request.course
    if not course:
        # public view
        course = request.collaboration_context.content_object
        public_url = project.public_url()
    else:
        # versioned view
        public_url = reverse('project-view-readonly', kwargs = { 'project_id': project.id, 'version_number': version_number})
        
    if not request.is_ajax():
        data['project'] = project
        data['version'] = version_number
        data['public_url'] = public_url
        return render_to_response('projects/project.html', data, context_instance=RequestContext(request))
    else:
        version = get_object_or_404(ProjectVersion,
                                    versioned_id = project_id,
                                    version_number=version_number)
        
        project = version.instance()
        
        panels = []
            
        # Requested project, either assignment or composition
        project_context = project_json(request, project, False, version_number)
        panel = { 'panel_state': 'open', 'panel_state_label': "Version View", 'context': project_context, 'template': 'project' }
        panels.append(panel)
        
        data['panels'] = panels
        
        return HttpResponse(simplejson.dumps(data, indent=2), mimetype='application/json')
      
@allow_http("GET")
def project_workspace(request, project_id, feedback=None):
    """
    A multi-panel editable view for the specified project
    Legacy note: Ideally, this function would be named project_view but
    StructuredCollaboration requires the view name to be  <class>-view to do a reverse        
    
    Panel 1: Parent Assignment (if applicable)
    Panel 2: Project
    Panel 3: Instructor Feedback (if applicable & exists) 
    
    Keyword arguments:
    project_id -- the model id
    
    """    
    project = get_object_or_404(Project, pk=project_id)
    
    if not project.can_read(request):
        return HttpResponseForbidden("forbidden")
    
    show_feedback = feedback == "feedback"
    data = { 'space_owner' : request.user.username, 'show_feedback': show_feedback }
    course = request.course
    is_faculty = course.is_faculty(request.user)
    
    if not request.is_ajax():
        data['project'] = project
        return render_to_response('projects/project.html', data, context_instance=RequestContext(request))
    else:
        panels = []
        
        is_assignment = project.is_assignment(request)
        can_edit = project.can_edit(request)
        feedback_discussion = project.feedback_discussion() if is_faculty or can_edit else None
    
        # Project Parent (assignment) if exists
        parent_assignment = project.assignment()
        if parent_assignment:
            assignment_context = project_json(request, parent_assignment, parent_assignment.can_edit(request))
            assignment_context['create_selection'] = True
            panel = { 'panel_state': 'closed', 'context': assignment_context, 'template': 'project' }
            panels.append(panel)
                    
        # Requested project, can be either an assignment or composition
        project_context = project_json(request, project, can_edit)
        project_context['editing'] = len(project.body) < 1 # only editing if it's new
        project_context['create_assignment_response'] = is_assignment and not is_faculty and in_course(request.user.username, course) and \
            not project.responses_by(request, request.user)
        project_context['create_instructor_feedback'] = is_faculty and parent_assignment and not feedback_discussion
        
        panel = { 'panel_state': 'closed' if show_feedback else 'open', 'context': project_context, 'template': 'project' }
        panels.append(panel)
        
        # Project Response -- if the requested project is an assignment
        # This is primarily a student view. The student's response should 
        # pop up automatically when the parent assignment is viewed.
        if is_assignment:
            responses = project.responses_by(request, request.user)
            if len(responses) > 0:
                response = responses[0]
                response_can_edit = response.can_edit(request)
                response_context = project_json(request, response, response_can_edit)
                
                panel = { 'panel_state': 'closed', 'context': response_context, 'template': 'project' }
                panels.append(panel)
                
                if not feedback_discussion and response_can_edit:
                    feedback_discussion = response.feedback_discussion()
            
        data['panels'] = panels
        
        # If feedback exists for the requested project
        if feedback_discussion:
            # 3rd pane is the instructor feedback, if it exists
            panel = { 'panel_state': 'open' if show_feedback else 'closed',
                      'panel_state_label': "Feedback",
                      'template': 'discussion',
                      'context': threaded_comment_json(feedback_discussion, request.user)
                    }
            panels.append(panel)
            
        return HttpResponse(simplejson.dumps(data, indent=2), mimetype='application/json')
    
def project_json(request, project, can_edit, version_number=None):
    '''
        JSON representation for a project. Includes:
        * basic project information
        * assets
        * annotations
        * responses (if applicable & permissable)
        * revisions (if permissable)
        * a project participant form (if permissable)
    '''
    
    rand = ''.join([choice(letters) for i in range(5)])
    
    versions = project.versions.order_by('-change_time')
    participants = project.attribution_list()
    
    data = { 'project': { 'title': project.title,
                          'body': project.body,
                          'participants': [{ 'name': p.get_full_name(),
                                             'username': p.username,
                                             'public_name': get_public_name(p, request),
                                             'is_viewer': request.user.username == p.username,
                                             'last':  idx == (len(participants) - 1) 
                                            } for idx, p in enumerate(participants)],
                          'id': project.pk,
                          'url': project.get_absolute_url(),
                          'public_url': project.public_url(),
                          'visibility': project.visibility(),
                          'username': request.user.username,
                          'type': 'assignment' if project.is_assignment(request) else 'composition',
                          'current_version': version_number if version_number else versions[0].version_number,
                          'create_selection': True if project.is_assignment(request) else False
                       },
            'assets': dict([('%s_%s' % (rand,ann.asset.pk),
                            ann.asset.sherd_json(request)
                            ) for ann in project.citations()
                           if ann.title and ann.title != "Annotation Deleted" and ann.title != 'Asset Deleted'
                           ]),
            'annotations': [ ann.sherd_json(request, rand, ('title','author')) 
                                for ann in project.citations()
                           ],
            'type': 'project',
            'can_edit': can_edit
    }
    
    data['responses'] = []
    for r in project.responses(request):
        if r.can_read(request):
            obj = { 'url': r.get_absolute_url(),
                    'title': r.title,
                    'modified': r.modified.strftime("%m/%d/%y %I:%M %p"),
                    'attribution_list': [] }
            
            x = len(r.attribution_list()) - 1
            for idx, author in enumerate(r.attribution_list()):
                obj['attribution_list'].append({ 'name': get_public_name(author, request),
                                                 'last': idx == x }) 
                
            data['responses'].append(obj)
    
    if project.is_participant(request.user):
        data['revisions'] = [{ 'version_number': v.version_number,
                               'versioned_id': v.versioned_id,
                               'author': get_public_name(v.instance().author, request),
                               'modified': v.modified.strftime("%m/%d/%y %I:%M %p") }
                              for v in versions ]
                              
    if can_edit:
        projectform = ProjectForm(request, instance=project)
        data['form'] = { 'participants': projectform['participants'].__unicode__(), 'publish': projectform['publish'].__unicode__() }
        
    return data
