from djangohelpers.lib import rendered_with
from djangohelpers.lib import allow_http

from django.db.models import get_model

from datetime import datetime

from structuredcollaboration.models import Collaboration
from django.http import HttpResponseForbidden, HttpResponseServerError
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse,resolve
from django.contrib.contenttypes.models import ContentType
from threadedcomments import ThreadedComment

from courseaffils.lib import in_course_or_404
from courseaffils.models import Course
from django.http import HttpResponseRedirect


from assetmgr.lib import most_popular,annotated_by

Asset = get_model('assetmgr','asset')


def show(request, discussion_id):
    """Show a threadedcomments discussion of an arbitrary object.
    discussion_id is the pk of the root comment."""
    root_comment = get_object_or_404(ThreadedComment, pk=discussion_id)
    return show_discussion(request, root_comment)


def show_collaboration(request, collab_id):
    collab_type = ContentType.objects.get_for_model(Collaboration)
    root_comment = get_object_or_404(ThreadedComment, 
                                     object_pk=collab_id, content_type = collab_type)
    return show_discussion(request, root_comment)

@allow_http("GET")
@rendered_with('discussions/show_discussion.html')
def show_discussion(request, root_comment):
    user = request.user
    if user.is_staff and request.GET.has_key('as'):
        user = get_object_or_404(User,username=request.GET['as'])

    #for_now:
    space_viewer = user
    space_owner = user
    
    if not root_comment.content_object.permission_to('read',request):
        return HttpResponseForbidden('You do not have permission to view this discussion.')
    
    try:
        my_course = root_comment.content_object.context.content_object
    except:
        #legacy: for when contexts weren't being set in new()
        my_course = request.course
        root_comment.content_object.context = Collaboration.get_associated_collab(my_course)
        root_comment.content_object.save()

    if 'project'==root_comment.content_object._parent.content_type.model:
        ajax_switcher_url = reverse('annotations-fragment-none', args=['none'])
    else:
        ajax_switcher_url = reverse('annotations-fragment', args=[space_viewer.username])

    return {
        'is_space_owner': True,
        'edit_comment_permission': my_course.is_faculty(user),
        'space_owner': space_owner,
        'space_viewer': space_viewer,
        'root_comment': root_comment,
        'ajax_switcher_url':ajax_switcher_url,
        'page_in_edit_mode': True,
        }
        
@allow_http("POST")
def new(request):
    """Start a discussion of an arbitrary model instance."""
    rp = request.POST

    title = rp['comment_html']
    #Find the object we're discussing.
    the_content_type = ContentType.objects.get(app_label=rp['app_label'], model=rp['model'])
    assert the_content_type != None
    
    the_object = the_content_type.get_object_for_this_type(pk = rp['obj_pk'])
    assert the_object != None
    
    
    try:
        obj_sc = Collaboration.get_associated_collab(the_object)
    except Collaboration.DoesNotExist:
        obj_sc = Collaboration()
        #TODO: populate this collab with sensible auth defaults.
        obj_sc.content_object = the_object
        obj_sc.save()

    #sky: I think what I want to do is have the ThreadedComment
    #point to the_object
    #and the collaboration will point to the threaded root comment
    #that way, whereas, if we live in Collaboration-land, we can get to ThreadedComments
    # threaded comments can also live in it's own world without 'knowing' about SC
    # OTOH, threaded comment shouldn't be able to point to the regular object
    # until Collaboration says it's OK (i.e. has permissions)
    # ISSUE: how to migrate? (see models.py)

    #now create the CHILD collaboration object for the discussion to point at.
    #This represents the auth for the discussion itself.
    disc_sc = Collaboration(_parent=obj_sc,
                            title=title,
                            #or we could point it at the root threadedcomments object.
                            #content_object=None,
                            context=request.collaboration_context,
                            )
    disc_sc.policy = rp.get('publish',None)
    disc_sc.save()

    #finally create the root discussion object, pointing it at the CHILD.
    new_threaded_comment = ThreadedComment(parent=None,
                                           title=title,
                                           comment='',
                                           user=request.user,
                                           content_object=disc_sc)
    
    #TODO: find the default site_id
    new_threaded_comment.site_id = 1
    new_threaded_comment.save()

    disc_sc.content_object = new_threaded_comment
    disc_sc.save()

    return HttpResponseRedirect( "/discussion/show/%d" % new_threaded_comment.id )
    


@allow_http("POST")    
@rendered_with('comments/posted.html')
def comment_change(request, comment_id, next=None):
    "save comment, since comments/post only does add, no edit"
    comment = ThreadedComment.objects.get(pk=comment_id)

    if comment.content_object.permission_to('edit',request):
        comment.comment = request.POST['comment']
    elif comment.user == request.user:
        now = datetime.now()
        comment.comment = '<div class="postupdate">[Post updated at <time datetime="%s">%s</time>]</div>%s' % (
            now.isoformat(),
            now.strftime('%I:%M%p %D').lower(),
            request.POST['comment']
            )
    else:
        return HttpResponseForbidden('You do not have permission to edit this discussion.')

    if request.POST['title']:
        comment.title = request.POST['title']
        if not comment.parent:
            disc_sc = comment.content_object
            disc_sc.title = comment.title
            disc_sc.save()

    comment.save()
    return {
        'comment': comment,
        }
    
