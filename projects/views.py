from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.http import HttpResponseForbidden
from django.http import HttpResponse

from django.shortcuts import get_object_or_404


from django.db.models import get_model

from tagging.models import Tag
from tagging.utils import calculate_cloud

from assetmgr.lib import annotated_by
from assetmgr.views import filter_by, get_active_filters

import simplejson as json
from random import choice
from string import letters

Asset = get_model('assetmgr','asset')
SherdNote = get_model('djangosherd','sherdnote')
Project = get_model('projects','project')
ProjectVersion = get_model('projects','projectversion')
User = get_model('auth','user')
Group = get_model('auth','group')        

from courseaffils.lib import in_course_or_404, get_public_name, AUTO_COURSE_SELECT
from projects.forms import ProjectForm
from djangohelpers.lib import rendered_with
from djangohelpers.lib import allow_http


### VIEWS ###
@rendered_with('projects/project.html')
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
        return project_json(request, project)

    if isinstance(project, dict):
        assignment_responses = None
        discussions = None
        user_responses = None
    else:
        assignment_responses = project.responses(request)
        discussions = project.discussions(request)
        user_responses = project.responses_by(request, request.user)

    return {
        'is_space_owner': is_participant,
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
        return project_json(request, project)
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
            return project_json(request, project)
        return project_workspace(request, space_owner, project)

    if request.method == "DELETE":
        project.delete()
        return HttpResponseRedirect(
            reverse('your-space-records', args=[request.user.username]))

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
                return HttpResponse(json.dumps(
                        {'status':'success',
                         'revision':{
                                'id':v_num,
                                'url':reverse('project_version_preview',args=[project_id, v_num]),
                                'public_url':projectform.instance.public_url(),
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

def project_json(request,project):
    rand = ''.join([choice(letters) for i in range(5)])

    data = {'project':{'title':project.title,
                       'body':project.body,
                       'participants':[{'name':p.get_full_name(),
                                        'username':p.username,
                                        } for p in project.participants.all()],
                       'id':project.pk,
                       'url':project.get_absolute_url(),
                       'username':request.user.username,
                       },
            'assets':dict([('%s_%s' % (rand,ann.asset.pk),
                            ann.asset.sherd_json(request)
                            ) for ann in project.citations()
                           if ann.title != "Annotation Deleted"
                           ]),
            'annotations':[ann.sherd_json(request, rand, ('title','author') )
                           for ann in project.citations()
                           ],
            'type':'project',
            }
    json = json.dumps(data, indent=2)
    return HttpResponse(json,
                        mimetype='application/json')


def project_workspace_courselookup(project_id=None,**kw):
    if project_id:
        return Project.objects.get(pk=project_id).course

AUTO_COURSE_SELECT[project_readonly_view] = project_workspace_courselookup
AUTO_COURSE_SELECT[view_project] = project_workspace_courselookup


