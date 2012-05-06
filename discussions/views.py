from django.core import urlresolvers
from django.conf import settings
from django.db.models import get_model, Max
from djangohelpers.lib import rendered_with, allow_http

from datetime import datetime

from structuredcollaboration.models import Collaboration
from structuredcollaboration.views import delete_collaboration

from django.http import HttpResponseForbidden, HttpResponseServerError, HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.core.urlresolvers import reverse,resolve

from django.contrib import comments
from django.contrib.comments.models import COMMENT_MAX_LENGTH
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.contrib.comments.managers import CommentManager

from threadedcomments import ThreadedComment
from threadedcomments.util import annotate_tree_properties, fill_tree

from courseaffils.lib import in_course_or_404
from courseaffils.models import Course

import simplejson

def show(request, discussion_id):
    """Show a threadedcomments discussion of an arbitrary object.
    discussion_id is the pk of the root comment."""
    root_comment = get_object_or_404(ThreadedComment, pk=discussion_id)
    return show_discussion(request, root_comment)

@allow_http("GET","DELETE")
def show_discussion(request, root_comment):
    space_viewer = request.user

    if request.method == "DELETE":
        return delete_collaboration(request, root_comment.object_pk)

    if not root_comment.content_object.permission_to('read',request):
        return HttpResponseForbidden('You do not have permission to view this discussion.')
    
    try:
        my_course = root_comment.content_object.context.content_object
    except:
        #legacy: for when contexts weren't being set in new()
        my_course = request.course
        root_comment.content_object.context = Collaboration.get_associated_collab(my_course)
        root_comment.content_object.save()

    target = None
    if root_comment.content_object._parent_id and \
            root_comment.content_object._parent.object_pk:
        target = root_comment.content_object._parent

    rv = {
        'is_space_owner': True,
        'edit_comment_permission': my_course.is_faculty(space_viewer),
        'space_owner': space_viewer, #for now
        'space_viewer': space_viewer,
        'root_comment': root_comment,
        'target':target,        
        'COMMENT_MAX_LENGTH':COMMENT_MAX_LENGTH, #change this in settings.COMMENT_MAX_LENGTH
        }
    
    return render_to_response('discussions/discussion.html', rv, context_instance=RequestContext(request))
        
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
    if rp.get('inherit',None)=='true':
        disc_sc.group_id = obj_sc.group_id
        disc_sc.user_id = obj_sc.user_id
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
    
    if not request.is_ajax():
        return HttpResponseRedirect( "/discussion/show/%d" % new_threaded_comment.id )
    else:
        data = { 'panel_state': 'open', 
                 'panel_state_label': "Feedback",
                 'template': 'discussion',
                 'context': threaded_comment_json(new_threaded_comment, request.user)
               }
        return HttpResponse(simplejson.dumps(data, indent=2), mimetype='application/json')   
    
@allow_http("POST")    
@rendered_with('comments/posted.html')
def comment_change(request, comment_id, next=None):
    "save comment, since comments/post only does add, no edit"
    comment = ThreadedComment.objects.get(pk=comment_id)

    if comment.content_object.permission_to('manage',request):
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
    
    

def pretty_date(timestamp):
    """
    Get a datetime object or a int() Epoch timestamp and return a
    pretty string like 'an hour ago', 'Yesterday', '3 months ago',
    'just now', etc
    """
    from datetime import datetime
    now = datetime.now()
    diff = now - timestamp 
    
    second_diff = diff.seconds
    day_diff = diff.days
    ago = ""
    
    if day_diff == 0:
        if second_diff < 10:
            ago = "just now"
        elif second_diff < 60:
            ago = str(second_diff) + " seconds ago"
        elif second_diff < 120:
            ago =  "a minute ago"
        elif second_diff < 3600:
            ago = str( second_diff / 60 ) + " minutes ago"
        elif second_diff < 7200:
            ago = "an hour ago"
        elif second_diff < 86400:
            ago = str( second_diff / 3600 ) + " hours ago"
        
        return "%s (%s)" % (timestamp.strftime("%I:%M %p"), ago)
    elif day_diff == 1:
        ago = "(Yesterday)"
    elif day_diff < 14:
        ago = "(" + str(day_diff) + " days ago)"
        
    return "%s %s" % (timestamp.strftime("%m/%d/%Y %I:%M %p"), ago)
      
def threaded_comment_json(comment, viewer):
    coll = ContentType.objects.get_for_model(Collaboration)
    all = ThreadedComment.objects.filter(content_type=coll, object_pk=comment.content_object.pk, site__pk=settings.SITE_ID)
    
    all = fill_tree(all)
    all = annotate_tree_properties(all)
    
    current_parent_id = None
    thread = []
    for obj in all:
        data = { 'open': obj.open if hasattr(obj, "open") else None,
                 'close': [ i for i in obj.close ] if hasattr(obj, "close") else None,
                 'id': obj.id,
                 'author': obj.name,
                 'submit_date': pretty_date(obj.submit_date),
                 'title': obj.title,
                 'content': obj.comment,
               }
    
        if obj.user == viewer:
            data['can_edit'] = True
            
        thread.append(data)
    
    data = { 
        'type': 'discussion',
        'form': comments.get_form()(comment.content_object).__unicode__(),
        'editing': True,
        'can_edit': True,
        'discussion': {
            'id': comment.id,
            'max_length': COMMENT_MAX_LENGTH,
            'thread': thread
         }
    }
    return data    
