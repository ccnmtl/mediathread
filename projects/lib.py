import simplejson
from random import choice
from string import letters
from courseaffils.lib import get_public_name
from projects.models import Project
from projects.forms import ProjectForm

def homepage_project_json(request, project, can_edit):
    the_json = {}
    the_json['id'] = project.id
    the_json['title'] = project.title
    the_json['url'] = project.get_absolute_url()
    
    participants = project.attribution_list()
    the_json['authors'] = [{
        'name': get_public_name(u, request),
        'last': idx == (len(participants) - 1) 
    } for idx, u in enumerate(participants)]
    the_json['modified'] = project.modified.strftime("%m/%d/%y %I:%M %p")
    the_json['status'] = project.status()
    the_json['editable'] = can_edit
    
    feedback = project.feedback_discussion()
    if feedback:
        the_json['feedback'] = feedback.id
        
    parent_assignment = project.assignment()
    if parent_assignment:    
        the_json['collaboration'] = {}
        the_json['collaboration']['title'] = parent_assignment.title
        the_json['collaboration']['url'] = parent_assignment.get_absolute_url()
        
    return the_json

def composition_project_json(request, project, can_edit, version_number=None):
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
    is_assignment = project.is_assignment(request)
    
    data = { 'project': { 'id': project.pk,
                          'title': project.title,
                          'url': project.get_absolute_url(),
                          'body': project.body,
                          'participants': [{ 'name': p.get_full_name(),
                                             'username': p.username,
                                             'public_name': get_public_name(p, request),
                                             'is_viewer': request.user.username == p.username,
                                             'last':  idx == (len(participants) - 1) 
                                            } for idx, p in enumerate(participants)],
                          
                          
                          'public_url': project.public_url(),
                          'visibility': project.visibility_short(),
                          'username': request.user.username,
                          'type': 'assignment' if is_assignment else 'composition',
                          'current_version': version_number if version_number else None,
                          'create_selection': is_assignment,
                          'is_assignment': is_assignment
                       },
            'assets': dict([('%s_%s' % (rand,ann.asset.pk),
                            ann.asset.sherd_json(request)
                            ) for ann in project.citations()
                           if ann.title != "Annotation Deleted" and ann.title != 'Asset Deleted'
                           ]),
            'annotations': [ ann.sherd_json(request, rand, ('title','author')) 
                                for ann in project.citations()
                           ],
            'type': 'project',
            'can_edit': can_edit,
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
    data['response_count'] = len(data['responses'])
    
    my_responses = []
    for r in project.responses_by(request, request.user):
        obj = { 'url': r.get_absolute_url(),
                'title': r.title,
                'modified': r.modified.strftime("%m/%d/%y %I:%M %p"),
                'attribution_list': [] }
        
        x = len(r.attribution_list()) - 1
        for idx, author in enumerate(r.attribution_list()):
            obj['attribution_list'].append({ 'name': get_public_name(author, request),
                                             'last': idx == x }) 
            
        my_responses.append(obj)
        
    if len(my_responses) == 1:
        data['my_response'] = my_responses[0]
    elif len(my_responses) > 1:
        data['my_responses'] = my_responses
        data['my_responses_count'] = len(my_responses)
    
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