
from djangohelpers.lib import rendered_with
from djangohelpers.lib import allow_http

from django.db.models import get_model


from discussions.models import Discussion
from structuredcollaboration.models import Collaboration
from django.http import HttpResponseForbidden, HttpResponseServerError
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse,resolve
from django.contrib.contenttypes.models import ContentType
from threadedcomments import ThreadedComment

from courseaffils.lib import in_course_or_404
from projects.forms import ProjectForm
from projects.models import Project
from courseaffils.models import Course


from assetmgr.lib import most_popular,annotated_by

import pdb

# tree management (add/remove leaf)
# re-ordering
# DO NOT PROVIDE 'MOVE' (intended to be unoptimized)


Asset = get_model('assetmgr','asset')




#TODO: refactor-- obj_id is actually going to be discussion_id
@rendered_with('discussions/class_discussion.html')
@allow_http("GET")
def show(request, obj_id):
    """View a discussion."""
    space_viewer = request.user
    if request.GET.has_key('as') and request.user.is_staff:
        space_viewer = get_object_or_404(User, username=request.GET['as'])
    #for now just for testing, get it working without space_viewer.
    my_course = None
    if request.course:
        my_course = request.course
    else:   
        my_courses = [c for c in Course.objects.all() if request.user in c.members]
        my_course = my_courses[-1]

    root_comment = get_object_or_404(ThreadedComment, pk = obj_id)
    #todo: figure out what space_viewer is.
    #TODO: figure out why request.course isn't populated.


    assets = annotated_by(Asset.objects.filter(course=my_course), request.user)
    #assets = annotated_by(Asset.objects.filter(course=request.course), space_viewer)
    return {
        'is_space_owner': True,
        'space_owner': request.user,
        'space_viewer': space_viewer,
        'root_comment': root_comment,
        'assets': assets,
        'page_in_edit_mode': True,
        }
