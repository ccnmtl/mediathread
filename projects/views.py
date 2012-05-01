import simplejson
from random import choice
from string import letters

from django.core.urlresolvers import reverse
from django.db.models import get_model
from django.http import HttpResponseRedirect, HttpResponseForbidden, HttpResponse, Http404
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from djangohelpers.lib import allow_http

from discussions.utils import threaded_comment_json
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
        project_context = project_json(request, request.course, is_faculty, project, project.can_edit(request))    
        project_context['editing'] = True
        
        data = { 'panel_state': 'open', 
                 'panel_state_label': "Edit",
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
            if "Preview" == request.POST.get('submit',None):
                #doesn't send project.author, and other non-exposed fields
                mock_project = projectform.cleaned_data.copy()
                mock_project['attribution_list'] = mock_project['participants']
                mock_project['assignment'] = projectform.instance.assignment()
                mock_project['id'] = project_id
                return project_preview(request, space_owner, mock_project, 
                                       is_participant=True, preview_num=request.GET.get('preview',1))
            
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
    

@allow_http("GET", "POST")
def project_delete(request, project_id):
    project = get_object_or_404(Project, pk=project_id,
                                course=request.course)
    space_owner = in_course_or_404(project.author.username, request.course)
    
    if not project.can_edit(request) or not request.method == "POST":
        return HttpResponseRedirect(project.get_absolute_url())

    project.delete()
    return HttpResponseRedirect('.')    
    
@allow_http("GET")
def project_workspace(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    
    if not project.can_read(request):
        return HttpResponseForbidden("forbidden")
    
    data = { 'space_owner' : request.user.username }
    course = request.course
    is_faculty = course.is_faculty(request.user)
    
    if not request.is_ajax():
        data['project'] = project
        return render_to_response('projects/project.html', data, context_instance=RequestContext(request))
    else:
        panels = []
        
        feedback = project.feedback_discussion()
    
        # Project Parent (assignment) if exists
        assignment = project.assignment()
        if assignment:
            assignment_context = project_json(request, course, is_faculty, assignment, assignment.can_edit(request))
            assignment_context['editing'] = False # Never editing by default
            assignment_context['create_assignment_response'] = False # obviously, we already have a response
            assignment_context['create_instructor_feedback'] = False
            assignment_context['create_selection'] = True
            panel = { 'panel_state': 'closed', 'panel_state_label': 'View', 'context': assignment_context, 'template': 'project' }

            panels.append(panel)
                    
        # Requested project, either assignment or composition
        is_assignment = project.is_assignment(request)
        can_edit = project.can_edit(request)
        project_context = project_json(request, course, is_faculty, project, can_edit)
        project_context['editing'] = can_edit # Always editing if it's allowed.
        project_context['create_assignment_response'] = is_assignment and not is_faculty and in_course(request.user.username, course) and \
            not project.responses_by(request, request.user)
        project_context['create_instructor_feedback'] = is_faculty and not is_assignment and \
            project.assignment() and not feedback  
        panel_state_label = "Edit" if can_edit else "View"   
        
        panel = { 'panel_state': 'open', 'panel_state_label': panel_state_label, 'context': project_context, 'template': 'project' }
        panels.append(panel)
        
        # Assignment response for requester if one exists
        if is_assignment:
            responses = project.responses_by(request, request.user)
            if len(responses) > 0:
                response = responses[0]
                response_context = project_json(request, course, is_faculty, response, response.can_edit(request))
                response_context['editing'] = False # Never editing by default
                response_context['create_assignment_response'] = False
                response_context['create_instructor_feedback'] = False  
                
                panel = { 'panel_state': 'closed', 'panel_state_label': 'View', 'context': response_context, 'template': 'project' }
                panels.append(panel)
            
        data['panels'] = panels
        
        if feedback:
            # 3rd pane is the instructor feedback, if it exists
            panel = { 'panel_state': 'open' if is_faculty else 'closed',
                      'panel_state_label': "Feedback",
                      'template': 'discussion',
                      'context': threaded_comment_json(feedback)
                    }
            panels.append(panel)
            
        return HttpResponse(simplejson.dumps(data, indent=2), mimetype='application/json')

@allow_http("GET")
def project_view_readonly(request, project_id, version_number=None):
    project = get_object_or_404(Project, pk = project_id)
    
    if not project.can_read(request):
        return HttpResponseForbidden("forbidden")
    
    if not version_number:
        versions = project.versions.order_by('-change_time')
        version_number = versions[0].version_number
    
    data = { 'space_owner' : request.user.username }
    
    course = request.course
    if not course:
        course = request.collaboration_context.content_object
        public_url = project.public_url()
    else:
        public_url = reverse('project-view-readonly', kwargs = { 'project_id': project.id, 'version_number': version_number})
        
    if not request.is_ajax():
        data['project'] = project
        data['version'] = version_number
        data['public_url'] = public_url
        return render_to_response('projects/project.html', data, context_instance=RequestContext(request))
    else:
        is_faculty = course.is_faculty(request.user)
    
        version = get_object_or_404(ProjectVersion,
                                    versioned_id = project_id,
                                    version_number=version_number)
        
        project = version.instance()
        
        panels = []
            
        # Requested project, either assignment or composition
        is_assignment = project.is_assignment(request)
        project_context = project_json(request, course, is_faculty, project, False)
        project_context['project']['current_version'] = version_number
        project_context['editing'] = False
        panel = { 'panel_state': 'open', 'panel_state_label': "Version View", 'context': project_context, 'template': 'project' }
        panels.append(panel)
        
        data['panels'] = panels
        
        return HttpResponse(simplejson.dumps(data, indent=2), mimetype='application/json')  
    
def project_json(request, course, is_faculty, project, can_edit):
    
    #bad language, we should change this to user_of_assets or something
    space_viewer = request.user 
        
    rand = ''.join([choice(letters) for i in range(5)])
    
    versions = project.versions.order_by('-change_time')
    
    data = { 'project': { 'title': project.title,
                          'body': project.body,
                          'participants': [{ 'name': p.get_full_name(),
                                             'username': p.username,
                                             'public_name': get_public_name(p, request),
                                             'is_viewer': space_viewer.username == p.username,  
                                            } for p in project.attribution_list()],
                          'id': project.pk,
                          'url': project.get_absolute_url(),
                          'public_url': project.public_url(),
                          'visibility': project.visibility(),
                          'username': request.user.username,
                          'type': 'assignment' if project.is_assignment(request) else 'composition',
                          'current_version': versions[0].version_number
                       },
            'assets': dict([('%s_%s' % (rand,ann.asset.pk),
                            ann.asset.sherd_json(request)
                            ) for ann in project.citations()
                           if ann.title and ann.title != "Annotation Deleted" and ann.title != 'Asset Deleted'
                           ]),
            'annotations': [ ann.sherd_json(request, rand, ('title','author')) 
                                for ann in project.citations()
                           ],
            'responses': [ { 'url': r.get_absolute_url(),
                             'title': r.title,
                             'attribution_list': [ { 'name': get_public_name(p, request) } for p in r.attribution_list() ],
                           } for r in project.responses(request)],
            'type': 'project',
            'can_edit': can_edit
    }
    
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
