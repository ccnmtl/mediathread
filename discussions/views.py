
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
from django.http import HttpResponseRedirect


from assetmgr.lib import most_popular,annotated_by

import pdb

Asset = get_model('assetmgr','asset')

@rendered_with('discussions/show_discussion.html')
@allow_http("GET")
def show(request, discussion_id):
    """View a class discussion."""
    root_comment = get_object_or_404(ThreadedComment, pk = discussion_id)

    space_viewer = request.user
    if request.GET.has_key('as') and request.user.is_staff:
        space_viewer = get_object_or_404(User, username=request.GET['as'])
    # TODO: figure out what space_viewer is.
    my_course = None
    if 1 == 0:
        #get the course will actually be from the context of the SC of the discussion.
        my_course = root_comment.content_object.context.content_object
    
    else:
        if request.course:
            my_course = request.course
        else:   
            my_courses = [c for c in Course.objects.all() if request.user in c.members]
            my_course = my_courses[-1]
    
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
        
        


@allow_http("POST")
def new(request):
    """Start a discussion of an arbitrary model instance."""
    #pdb.set_trace()
    rp = request.POST
    app_label, model, obj_pk, comment_html =  ( rp['app_label'], rp['model'], rp['obj_pk'], rp['comment_html'] )
    #Find the object we're discussing.
    the_content_type = ContentType.objects.get(app_label=app_label, model=model)
    assert the_content_type != None
    
    the_object = the_content_type.get_object_for_this_type(pk = obj_pk)
    assert the_object != None
    
    #if the discussed object doesn't have a Collaboration associated with it, create one.
    #TODO: use create_or_get. Is nicer.
    
    try:
        obj_sc = Collaboration.get_associated_collab(the_object)
    except Collaboration.DoesNotExist:
        obj_sc = Collaboration()
        #TODO: populate this collab with sensible auth defaults.
        obj_sc.content_object = the_object
        obj_sc.save()
    
    #now create the CHILD collaboration object for the discussion to point at.
    #This represents the auth for the discussion itself.
    disc_sc = Collaboration()
    disc_sc._parent = obj_sc
    disc_sc.title = "Discussion of %s" % the_object
    disc_sc.content_object = None #or we could point it at the root threadedcomments object.
    disc_sc.save()

    #finally create the root discussion object, pointing it at the CHILD.
    #TODO point the context at the course
    new_threaded_comment = ThreadedComment()
    new_threaded_comment.parent = None
    new_threaded_comment.comment = comment_html    
    new_threaded_comment.user = request.user
    new_threaded_comment.content_object = disc_sc
    
    #TODO: find the default site_id
    new_threaded_comment.site_id = 1
    new_threaded_comment.save()
    return HttpResponseRedirect( "/discussion/show/%d" % new_threaded_comment.id )
    
    


#TODO: why is this attempt to override comment_posted not working?
@rendered_with('discussions/class_discussion.html')
@allow_http("GET")
def my_comment_posted( request ):
    #if request.GET['c']:
    #    comment_id, post_id  = request.GET['c'].split( ':' )
    #    post = Post.objects.get( pk=post_id )
    #
    #    if post:
    #        return HttpResponseRedirect( post.get_absolute_url() )
    #
    #return HttpResponseRedirect( "/" )
    return HttpResponseRedirect( "/discussion/show/310" )
    
    
    
