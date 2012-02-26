from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.http import HttpResponseForbidden
from django.http import HttpResponse

from django.shortcuts import get_object_or_404
from django.shortcuts import render_to_response
from django.template import RequestContext

from django.db.models import get_model

from tagging.models import Tag
from tagging.utils import calculate_cloud

from assetmgr.lib import annotated_by
from assetmgr.views import filter_by, get_active_filters

import simplejson
from random import choice
from string import letters

Asset = get_model('assetmgr','asset')
SherdNote = get_model('djangosherd','sherdnote')
Project = get_model('projects','project')
ProjectVersion = get_model('projects','projectversion')
User = get_model('auth','user')
Group = get_model('auth','group')        

from courseaffils.lib import in_course_or_404, in_course, get_public_name, AUTO_COURSE_SELECT
from projects.forms import ProjectForm
from djangohelpers.lib import rendered_with
from djangohelpers.lib import allow_http


### VIEWS ###
@rendered_with('projects/edit_project.html')
def project_workspace(request, user, project):
    space_viewer = request.user
    if request.GET.has_key('as') and request.user.is_staff:
        space_viewer = get_object_or_404(User, username=request.GET['as'])

    projectform = ProjectForm(request, instance=project)
    return {
        'is_space_owner': project.is_participant(user),
        'space_owner': user,
        'space_viewer': space_viewer,
        'project': project,
        'projectform': projectform,
        'page_in_edit_mode': True,
    }

@rendered_with('projects/published_project.html')
def project_preview(request, user, project, is_participant=None, preview_num=0):
    if is_participant is None:
        is_participant = project.is_participant(user) 
    course = request.collaboration_context.content_object
    
    if request.META.get('HTTP_ACCEPT','').find('json') >=0:
        return project_json_response(request, project)

    is_assignment_owner = False
    
    if isinstance(project, dict):
        assignment_responses = None
        discussions = None
        user_responses = None
    else:
        assignment_responses = project.responses(request)
        discussions = project.discussions(request)
        user_responses = project.responses_by(request, request.user)

        if project.assignment():
            is_assignment_owner = project.assignment().is_participant(user)
        
    return {
        'is_space_owner': is_participant,
        'is_assignment_owner': is_assignment_owner,
        'project': project,
        'is_preview': preview_num,
        'preview_num': preview_num,
        'is_faculty': course.is_faculty(request.user),
        'assignment_responses': assignment_responses,
        'discussions': discussions,
        'user_responses': user_responses,
        #'space_owner':project.author, #was there for project_readonly_view()
        }

@rendered_with('projects/published_project.html')
def project_version_preview(request, project_id, version_number, check_permission=True):
    project = get_object_or_404(Project,pk = project_id)

    if check_permission and \
            not project.is_participant(request.user) \
            and not request.course.is_faculty(request.user) \
            and not request.user.is_staff:
        return HttpResponseForbidden("forbidden")    
    version = get_object_or_404(ProjectVersion,
                                versioned_id = project_id,
                                version_number=version_number,
                                )
    project = version.instance()
    if request.META.get('HTTP_ACCEPT','').find('json') >=0:
        return project_json_response(request, project)
    return {
        'is_space_owner': project.is_participant(request.user),
        'project': project,
        'version_number': int(version_number),
        'assignment_responses': project.responses(request),
        'discussions': project.discussions(request),
        }
        
def project_version_view(request, projectversion_id, check_permission=True):
    pv = get_object_or_404(ProjectVersion,
                           pk=projectversion_id)
    return project_version_preview(request, 
                                   pv.versioned_id, 
                                   pv.version_number, 
                                   check_permission=check_permission)


@allow_http("GET")
def project_readonly_view(request, project_id, check_permission=True):
    course = request.collaboration_context.content_object
    project = get_object_or_404(Project, pk=project_id,
                                course=course)

    if not project.visible(request):
        return HttpResponseForbidden("forbidden")

    return project_preview(request, request.user, project)

def project_workspace_courselookup(project_id=None,**kw):
    if project_id:
        return Project.objects.get(pk=project_id).course

@allow_http("GET", "POST", "DELETE")
def view_project(request, project_id):
    project = get_object_or_404(Project, pk=project_id,
                                course=request.course)
    space_owner = in_course_or_404(project.author.username, request.course)

    if not project.collaboration(request).permission_to('edit',request):
        #LEGACY: try again for legacy projects
        if not project.collaboration(request, sync_group=True).permission_to('edit',request):
            return HttpResponseRedirect(project.get_absolute_url())

    if request.method == "GET":
        if request.META.get('HTTP_ACCEPT','').find('json') >=0:
            return project_json_response(request, project)
        return project_workspace(request, space_owner, project)

    if request.method == "DELETE":
        project.delete()
        return HttpResponseRedirect(
            reverse('your-records', args=[request.user.username]))

    if request.method == "POST":
        projectform = ProjectForm(request, instance=project,data=request.POST)
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
                                'id':v_num,
                                'url':reverse('project_version_preview',args=[project_id, v_num]),
                                'public_url':projectform.instance.public_url(),
                                'visibility': project.visibility()
                                }
                         }, indent=2),
                                    mimetype='application/json')

        redirect_to = '.'
        return HttpResponseRedirect(redirect_to)

@rendered_with('projects/your_projects.html')
@allow_http("GET", "POST")
def your_projects(request, user_name):
    in_course_or_404(user_name, request.course)
    
    user = get_object_or_404(User, username=user_name)

    editable = user==request.user

    if request.method == "GET":
        projects = Project.get_user_projects(user, request.course).order_by('modified')
        if not editable:
            projects = [p for p in projects if p.visible(request)]

        try:
            initially_expanded_project = int(request.GET['show'])
        except:
            if len(projects):
                initially_expanded_project = projects[0].pk
            else:
                initially_expanded_project = None
        
        return {
            'projects': projects,
            'editable': editable,
            'space_owner': user,
            'initially_expanded_project': initially_expanded_project,
            }

    if request.method == "POST":
        if not editable:
            return HttpResponseForbidden("forbidden")
        
        title = request.POST.get('title','') or "Untitled" 
        project = Project(author=user, course=request.course, title=title)
        project.save()

        project.collaboration(request, sync_group=True)

        parent = request.POST.get("parent")
        if parent is not None:
            try:
                parent = Project.objects.get(pk=parent)
            except Project.DoesNotExist:
                parent = None
                return HttpResponseRedirect(project.get_workspace_url())

            parent_collab = parent.collaboration(request)
            if parent_collab.permission_to("add_child", request):
                parent_collab.append_child(project)
                
        return HttpResponseRedirect(project.get_workspace_url())

def project_json_response(request,project):
    data = project_json(request, project)
    HttpResponse(simplejson.dumps(data, indent=2), mimetype='application/json')
    
@allow_http("GET")
def project_panel_view(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    
    if not project.can_read(request):
        return HttpResponseForbidden("forbidden")
    
    course = request.course
    is_faculty = course.is_faculty(request.user)
    
    data = {}
    
    if not request.is_ajax():
        data['project'] = project
        return render_to_response('projects/project.html', data, context_instance=RequestContext(request))
    else:
        panels = []
    
        # Project Parent (assignment) if exists
        assignment = project.assignment()
        if assignment:
            can_edit = assignment.can_edit(request)
            assignment_context = project_json(request, assignment)
            assignment_context['can_edit'] = can_edit
            assignment_context['editing'] = False # Never editing by default
            assignment_context['create_assignment_response'] = False # obviously, we already have a response
            assignment_context['create_instructor_feedback'] = False
            assignment_context['create_selection'] = True
            panel = { 'panel_state': 'closed', 'panel_state_label': 'View', 'context': assignment_context, 'template': 'project' }
            if can_edit:
                projectform = ProjectForm(request, instance=assignment)
                assignment_context['form'] = { 'participants': projectform['participants'].__unicode__(), 'publish': projectform['publish'].__unicode__() }

            panels.append(panel)
                    
        # Requested project, either assignment or composition
        is_assignment = project.is_assignment(request)
        can_edit = project.can_edit(request)
        project_context = project_json(request, project)
        project_context['editing'] = can_edit # Always editing if it's allowed.
        project_context['can_edit'] = can_edit
        project_context['create_assignment_response'] = is_assignment and not is_faculty and in_course(request.user.username, course) and \
            not project.responses_by(request, request.user)
        project_context['create_instructor_feedback'] = is_faculty and not is_assignment and \
            project.assignment() and not project.feedback_discussion()  
        
        if can_edit:
            projectform = ProjectForm(request, instance=project)
            p = projectform['participants']
            s = p.__str__()
            u = p.__unicode__()
            t = '%s' % p
            project_context['form'] = { 'participants': projectform['participants'].__unicode__(), 'publish': projectform['publish'].__unicode__() }
        
        panel = { 'panel_state': 'open', 'panel_state_label': 'Edit', 'context': project_context, 'template': 'project' }
        panels.append(panel)
        
        # Assignment response for requester if one exists
        if is_assignment:
            responses = project.responses_by(request, request.user)
            if len(responses) > 0:
                can_edit = response.can_edit(request)
                response = responses[0]
                response_context = project_json(request, response)
                response_context['editing'] = False # Never editing by default
                response_context['can_edit'] = can_edit
                response_context['create_assignment_response'] = False
                response_context['create_instructor_feedback'] = False  
                
                if can_edit:
                    projectform = ProjectForm(request, instance=response)
                    response_context['form'] = { 'participants': projectform['participants'].__unicode__(), 'publish': projectform['publish'].__unicode__() }
                
                panel = { 'panel_state': 'closed', 'panel_state_label': 'View', 'context': response_context, 'template': 'project' }
                panels.append(panel)
            
        data['panels'] = panels
        
        # 3rd pane is the instructor feedback, if it exists
        # TODO
            
        return HttpResponse(simplejson.dumps(data, indent=2), mimetype='application/json')
    
    
def project_json(request, project):
    #bad language, we should change this to user_of_assets or something
    space_viewer = request.user 
    if request.GET.has_key('as') and request.user.is_staff:
        space_viewer = get_object_or_404(User, username=request.GET['as'])
        
    rand = ''.join([choice(letters) for i in range(5)])
    
    data = {'project':{'title':project.title,
                       'body':project.body,
                       'participants':[{'name':p.get_full_name(),
                                        'username':p.username,
                                        'public_name': get_public_name(p, request),
                                        'is_viewer': space_viewer.username == p.username,  
                                        } for p in project.attribution_list()],
                       'id':project.pk,
                       'url':project.get_absolute_url(),
                       'public_url':project.public_url(),
                       'visibility': project.visibility(),
                       'username':request.user.username,
                       'type': 'assignment' if project.is_assignment(request) else 'composition', 
                       },
            'assets':dict([('%s_%s' % (rand,ann.asset.pk),
                            ann.asset.sherd_json(request)
                            ) for ann in project.citations()
                           if ann.title and ann.title != "Annotation Deleted" and ann.title != 'Asset Deleted'
                           ]),
            'annotations':[ann.sherd_json(request, rand, ('title','author') )
                           for ann in project.citations()
                           ],
            'responses': [ { 'url': r.get_absolute_url(),
                             'title': r.title,
                             'attribution_list': [ get_public_name(p, request) for p in r.attribution_list()],
                           } for r in project.responses(request)],
            'type':'project',
            }
    return data

AUTO_COURSE_SELECT[project_readonly_view] = project_workspace_courselookup
AUTO_COURSE_SELECT[view_project] = project_workspace_courselookup