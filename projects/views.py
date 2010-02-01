from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.http import HttpResponseForbidden
from django.http import HttpResponse

from django.shortcuts import get_object_or_404


from django.db.models import get_model

from tagging.models import Tag
from tagging.utils import calculate_cloud

from assetmgr.lib import annotated_by
import simplejson as json
from random import choice
import string

Asset = get_model('assetmgr','asset')
SherdNote = get_model('djangosherd','sherdnote')
Project = get_model('projects','project')
ProjectVersion = get_model('projects','projectversion')
User = get_model('auth','user')
        

from courseaffils.lib import in_course_or_404
from projects.forms import ProjectForm
from djangohelpers.lib import rendered_with
from djangohelpers.lib import allow_http

@rendered_with('projects/project.html')
def project_workspace(request, user, project):
    space_viewer = request.user
    if request.GET.has_key('as') and request.user.is_staff:
        space_viewer = get_object_or_404(User, username=request.GET['as'])

    assets = annotated_by(Asset.objects.filter(course=request.course),
                          space_viewer)

    projectform = ProjectForm(request, instance=project)
    
    return {
        'is_space_owner': project.is_participant(user),
        'space_owner': user,
        'space_viewer': space_viewer,
        'project': project,
        'projectform': projectform,
        'assets': assets,
        'page_in_edit_mode': True,
        }

@rendered_with('projects/published_project.html')
def project_preview(request, user, project):
    return {
        'is_space_owner': project.is_participant(user),
        'project': project,
        'is_preview': True,
        }
        
        

@rendered_with('projects/published_project.html')
def project_version_preview(request, project_id, version_number, check_permission=True):
    if check_permission and \
            not request.user.is_staff \
            and not project.is_participant(request.user) \
            and not request.course.is_faculty(request.user):
        return HttpResponseForbidden("forbidden")    
    version = get_object_or_404(ProjectVersion,
                                versioned_id = project_id,
                                version_number=version_number,
                                )
    project = version.instance()
    if request.META['HTTP_ACCEPT'].find('json') >=0:
        return project_json(request, project)
    return {
        'is_space_owner': project.is_participant(request.user),
        'project': project,
        'version_number': int(version_number),
        }
        
def project_version_view(request, projectversion_id, check_permission=True):
    pv = get_object_or_404(ProjectVersion,
                           pk=projectversion_id)
    return project_version_preview(request, 
                                   pv.versioned_id, 
                                   pv.version_number, 
                                   check_permission=check_permission)

@rendered_with('projects/published_project.html')
@allow_http("GET")
def project_readonly_view(request, project_id, check_permission=True):
    course = request.collaboration_context.content_object
    project = get_object_or_404(Project, pk=project_id,
                                course=course,
                                submitted=True)
    if request.META['HTTP_ACCEPT'].find('json') >=0:
        return project_json(request, project)
    return {
        'is_space_owner': project.is_participant(request),
        'space_owner': project.author,
        'project': project,
        'is_faculty': course.is_faculty(request.user),
        }

@allow_http("GET", "POST", "DELETE")
def view_project(request, project_id):
    project = get_object_or_404(Project, pk=project_id,
                                course=request.course)

    space_owner = in_course_or_404(project.author.username, request.course)

    if project not in Project.get_user_projects(space_owner,request.course):
        return HttpResponseForbidden("forbidden")



    if request.method == "DELETE":
        project.delete()
        return HttpResponseRedirect(
            reverse('your-space-records', args=[request.user.username]))

    if not project.is_participant(request.user):
        return project_readonly_view(request, project.id)
    #ok, now we know is_participant

    if request.method == "GET":
        return project_workspace(request, space_owner, project)
    
    if request.method == "POST":
        projectform = ProjectForm(request, instance=project,data=request.POST)
        redirect_to = '.'
        if projectform.is_valid():
            if "Submit"== request.POST.get('submit',None):
                projectform.instance.submitted = True
                redirect_to = reverse('your-space-records', args=[request.user.username])
                redirect_to += "?show=%d" % project.pk

            #this changes for version-tracking purposes
            projectform.instance.author = request.user
            projectform.save()

        if "Preview" == request.POST.get('submit',None):
            return project_preview(request, space_owner, project)

        return HttpResponseRedirect(redirect_to)

@rendered_with('projects/your_projects.html')
@allow_http("GET", "POST")
def your_projects(request, user_name):
    in_course_or_404(user_name, request.course)
    
    user = get_object_or_404(User, username=user_name)

    editable = user==request.user

    if request.method == "GET":
        projects = Project.get_user_projects(user, request.course)
        if not editable:
            projects = projects.filter(submitted=True)
        projects = projects.order_by('modified')

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
        
        title = request.POST.get('title','') or "%s's Project" % user.get_full_name()
        project = Project(author=user, course=request.course, title=title)
        project.save()
        return HttpResponseRedirect(project.get_absolute_url())

def project_json(request,project):
    rand = ''.join([choice(string.letters) for i in range(5)])
    data = {'project':{'title':project.title,
                       'body':project.body,
                       'participants':[{'name':p.get_full_name()} for p in project.participants.all()],
                       'id':project.pk,
                       },
            'assets':dict([('%s_%s' % (rand,ann.asset.pk),
                            {'sources':dict([(s.label, {
                                        'label':s.label,
                                        'url':s.url,
                                        'width':s.width,
                                        'height':s.height,
                                        'primary':s.primary
                                        }) for s in ann.asset.source_set.all()]),
                             'primary':ann.asset.primary.label,
                             'title':ann.asset.title, 
                             'metadata':json.loads(ann.asset.metadata_blob)
                             }
                            ) for ann in project.citations()]),
            
            'annotations':[
            {'asset_key':'%s_%s' % (rand,ann.asset_id),
             'id':ann.pk,
             'range1':ann.range1,
             'range2':ann.range2,
             'annotation':ann.annotation(),
             'title':ann.title,
             'author':{'id':ann.author_id,
                       'name':ann.author.get_full_name(),
                       },
             
             } for ann in project.citations()
            ]
            }
    return HttpResponse(json.dumps(data, indent=2),
                        mimetype='application/json')

