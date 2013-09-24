from courseaffils.lib import get_public_name
from mediathread.assetmgr.api import AssetSummaryResource
from mediathread.djangosherd.api import SherdNoteResource
from mediathread.projects.forms import ProjectForm
from random import choice
from string import letters


def homepage_assignment_json(assignments, is_faculty):
    return [{'id': a.id,
             'url': a.get_absolute_url(),
             'title': a.title,
             'display_as_assignment': True,
             'is_faculty': is_faculty,
             'due_date': a.get_due_date(),
             'modified_date': a.modified.strftime("%m/%d/%y"),
             'modified_time': a.modified.strftime("%I:%M %p")}
            for a in assignments]


def homepage_project_json(request, projects, can_edit):
    project_json = []

    for project in projects:
        the_json = {}
        the_json['id'] = project.id
        the_json['title'] = project.title
        the_json['url'] = project.get_absolute_url()
        the_json['due_date'] = project.get_due_date()

        participants = project.attribution_list()
        the_json['authors'] = [{
            'name': get_public_name(u, request),
            'last': idx == (len(participants) - 1)
        } for idx, u in enumerate(participants)]
        the_json['modified_date'] = project.modified.strftime("%m/%d/%y")
        the_json['modified_time'] = project.modified.strftime("%I:%M %p")
        the_json['status'] = project.status()
        the_json['editable'] = can_edit

        if can_edit:
            feedback = project.feedback_discussion()
            if feedback:
                the_json['feedback'] = feedback.id

        parent_assignment = project.assignment()
        if parent_assignment:
            the_json['collaboration'] = {}
            the_json['collaboration']['title'] = parent_assignment.title
            the_json['collaboration']['url'] = \
                parent_assignment.get_absolute_url()
            the_json['collaboration']['due_date'] = \
                parent_assignment.get_due_date()

        is_assignment = project.is_assignment(request)
        if is_assignment:
            count = 0
            for response in project.responses(request):
                if response.can_read(request):
                    count += 1
            the_json['responses'] = count

        the_json['display_as_assignment'] = \
            is_assignment or parent_assignment is not None

        if is_assignment:
            the_json['is_assignment'] = True
            the_json['responses'] = len(project.responses(request))

        project_json.append(the_json)

    return project_json


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

    participants = project.attribution_list()
    is_assignment = project.is_assignment(request)

    course = request.course if request.course \
        else request.collaboration_context.content_object

    asset_resource = AssetSummaryResource()
    sherd_resource = SherdNoteResource()
    citations = project.citations()

    data = {
        'project': {
            'id': project.pk,
            'title': project.title,
            'url': project.get_absolute_url(),
            'due_date': project.get_due_date(),
            'body': project.body,
            'participants': [{
                'name': p.get_full_name(),
                'username': p.username,
                'public_name': get_public_name(p, request),
                'is_viewer': request.user.username == p.username,
                'last': idx == (len(participants) - 1)
            } for idx, p in enumerate(participants)],
            'public_url': project.public_url(),
            'visibility': project.visibility_short(),
            'username': request.user.username,
            'type': 'assignment' if is_assignment else 'composition',
            'description': project.description(),
            'current_version': version_number if version_number else None,
            'create_selection': is_assignment,
            'is_assignment': is_assignment,
            'course_title': course.title
        },
        'type': 'project',
        'can_edit': can_edit,
        'annotations': [sherd_resource.render_one(request, ann, rand)
                        for ann in citations],
    }

    assets = {}
    for ann in citations:
        if ann.title != "Annotation Deleted" and ann.title != 'Asset Deleted':
            key = '%s_%s' % (rand, ann.asset.pk)
            if key not in assets:
                assets[key] = asset_resource.render_one(request, ann.asset)
    data['assets'] = assets

    data['responses'] = []
    for response in project.responses(request):
        if response.can_read(request):
            obj = {'url': response.get_absolute_url(),
                   'title': response.title,
                   'modified': response.modified.strftime("%m/%d/%y %I:%M %p"),
                   'attribution_list': []}

            last = len(response.attribution_list()) - 1
            for idx, author in enumerate(response.attribution_list()):
                obj['attribution_list'].append({
                    'name': get_public_name(author, request),
                    'last': idx == last})

            data['responses'].append(obj)
    data['response_count'] = len(data['responses'])

    my_responses = []
    for response in project.responses_by(request, request.user):
        obj = {'url': response.get_absolute_url(),
               'title': response.title,
               'modified': response.modified.strftime("%m/%d/%y %I:%M %p"),
               'attribution_list': []}

        last = len(response.attribution_list()) - 1
        for idx, author in enumerate(response.attribution_list()):
            obj['attribution_list'].append({'name': get_public_name(author,
                                                                    request),
                                            'last': idx == last})

        my_responses.append(obj)

    if len(my_responses) == 1:
        data['my_response'] = my_responses[0]
    elif len(my_responses) > 1:
        data['my_responses'] = my_responses
        data['my_responses_count'] = len(my_responses)

    if project.is_participant(request.user):
        data['revisions'] = [{
            'version_number': v.version_number,
            'versioned_id': v.versioned_id,
            'author': get_public_name(v.instance().author, request),
            'modified': v.modified.strftime("%m/%d/%y %I:%M %p")}
            for v in project.versions.order_by('-change_time')]

    if can_edit:
        projectform = ProjectForm(request, instance=project)
        data['form'] = {
            'participants': projectform['participants'].__unicode__(),
            'publish': projectform['publish'].__unicode__()
        }

    return data
