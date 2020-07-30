from datetime import datetime
import json
from random import choice
from string import ascii_letters

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponse, HttpResponseForbidden, \
    HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.utils.encoding import smart_text
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.generic.base import View
import django_comments
from django_comments.models import COMMENT_MAX_LENGTH
from djangohelpers.lib import rendered_with, allow_http
from mediathread.api import UserResource
from mediathread.assetmgr.api import AssetResource
from mediathread.discussions.utils import pretty_date
from mediathread.djangosherd.api import SherdNoteResource
from mediathread.djangosherd.models import DiscussionIndex
from mediathread.main.course_details import cached_course_collaboration
from mediathread.mixins import (
    LoggedInCourseMixin, LoggedInFacultyMixin
)
from mediathread.taxonomy.api import VocabularyResource
from mediathread.taxonomy.models import Vocabulary
from structuredcollaboration.models import Collaboration
from threadedcomments.models import ThreadedComment
from threadedcomments.util import annotate_tree_properties, fill_tree


class DiscussionCreateView(LoggedInFacultyMixin, View):

    def post(self, request, *args, **kwargs):

        """Start a discussion of an arbitrary model instance."""
        title = request.POST['comment_html']
        comment = request.POST.get('comment', '')

        # Find the object we're discussing.
        model = request.POST['model']
        the_content_type = ContentType.objects.get(
            app_label=request.POST['app_label'], model=model)
        assert the_content_type is not None

        the_object = the_content_type.get_object_for_this_type(
            pk=request.POST['obj_pk'])
        assert the_object is not None

        try:
            obj_sc = Collaboration.objects.get_for_object(the_object)
        except Collaboration.DoesNotExist:
            obj_sc = Collaboration()
            # TODO: populate this collab with sensible auth defaults.
            obj_sc.content_object = the_object
            obj_sc.save()

        # sky: I think what I want to do is have the ThreadedComment
        # point to the_object
        # and the collaboration will point to the threaded root comment
        # that way, whereas, if we live in Collaboration-land,
        # we can get to ThreadedComments
        # threaded comments can also live in it's own world without 'knowing'
        # about SC OTOH, threaded comment shouldn't be able
        # to point to the regular object
        # until Collaboration says it's OK (i.e. has permissions)
        # ISSUE: how to migrate? (see models.py)

        # now create the CHILD collaboration object for the
        # discussion to point at.
        # This represents the auth for the discussion itself.
        collaboration_context = cached_course_collaboration(request.course)
        disc_sc = Collaboration(_parent=obj_sc,
                                title=title,
                                # or we could point it at the root
                                # threadedcomments object.
                                # content_object=None,
                                context=collaboration_context,
                                )
        disc_sc.set_policy(request.POST.get('publish', None))
        disc_sc.save()

        # finally create the root discussion object, pointing it at the CHILD.
        new_threaded_comment = ThreadedComment(parent=None,
                                               title=title,
                                               comment=comment,
                                               user=request.user,
                                               content_object=disc_sc)

        # TODO: find the default site_id
        new_threaded_comment.site_id = 1
        new_threaded_comment.save()

        disc_sc.content_object = new_threaded_comment
        disc_sc.save()

        DiscussionIndex.update_class_references(
            new_threaded_comment.comment, new_threaded_comment.user,
            new_threaded_comment, new_threaded_comment.content_object,
            new_threaded_comment.user)

        if not request.is_ajax():
            if model == 'project':
                discussion_url = reverse(
                    'project-workspace',
                    args=(request.course.pk, the_object.pk))
            else:
                discussion_url = reverse(
                    'discussion-view',
                    args=(request.course.pk, new_threaded_comment.id))

            return HttpResponseRedirect(discussion_url)
        else:
            vocabulary = VocabularyResource().render_list(
                request, Vocabulary.objects.filter(course=request.course))

            user_resource = UserResource()
            owners = user_resource.render_list(request, request.course.members)

            data = {'panel_state': 'open',
                    'panel_state_label': "Instructor Feedback",
                    'template': 'discussion',
                    'owners': owners,
                    'vocabulary': vocabulary,
                    'context': threaded_comment_json(request,
                                                     new_threaded_comment)}

            return HttpResponse(json.dumps(data, indent=2),
                                content_type='application/json')


class DiscussionDeleteView(LoggedInFacultyMixin, View):
    def post(self, request, discussion_id):
        root_comment = get_object_or_404(ThreadedComment, pk=discussion_id)

        ctype = ContentType.objects.get_for_model(ThreadedComment)
        collaboration = get_object_or_404(Collaboration,
                                          content_type=ctype,
                                          object_pk=root_comment.pk)

        root_comment.delete()
        collaboration.delete()
        url = reverse('assignment-list', args=[request.course.id])
        return HttpResponseRedirect(url)


class DiscussionView(LoggedInCourseMixin, View):

    @method_decorator(ensure_csrf_cookie)
    def get(self, request, *args, **kwargs):
        """Show a threadedcomments discussion of an arbitrary object.
        discussion_id is the pk of the root comment."""

        discussion_id = kwargs.get('discussion_id', None)
        root_comment = get_object_or_404(ThreadedComment, pk=discussion_id)
        if not root_comment.content_object.permission_to(
                'read', request.course, request.user):
            return HttpResponseForbidden('You do not have permission \
                                         to view this discussion.')

        try:
            my_course = root_comment.content_object.context.content_object
        except AttributeError:
            # legacy: for when contexts weren't being set in new()
            my_course = request.course
            root_comment.content_object.context = \
                Collaboration.objects.get_for_object(my_course)
            root_comment.content_object.save()

        data = {'space_owner': request.user.username}

        if not request.is_ajax():
            data['discussion'] = root_comment
            return render(request, 'discussions/discussion.html', data)
        else:
            vocabulary = VocabularyResource().render_list(
                request, Vocabulary.objects.filter(course=request.course))

            user_resource = UserResource()
            owners = user_resource.render_list(request, request.course.members)

            data['panels'] = [{
                'panel_state': 'open',
                'subpanel_state': 'open',
                'panel_state_label': "Discussion",
                'template': 'discussion',
                'owners': owners,
                'vocabulary': vocabulary,
                'title': root_comment.title,
                'can_edit_title': my_course.is_faculty(request.user),
                'root_comment_id': root_comment.id,
                'context': threaded_comment_json(request, root_comment)
            }]

            # Create a place for asset editing
            panel = {'panel_state': 'closed',
                     'panel_state_label': "Item Details",
                     'template': 'asset_quick_edit',
                     'update_history': False,
                     'show_collection': False,
                     'owners': owners,
                     'vocabulary': vocabulary,
                     'context': {'type': 'asset'}}

            data['panels'].append(panel)

            return HttpResponse(json.dumps(data),
                                content_type='application/json')


@allow_http("POST")
@login_required
@rendered_with('comments/posted.html')
def comment_save(request, comment_id, next_url=None):
    "save comment, since comments/post only does add, no edit"
    comment = ThreadedComment.objects.get(pk=comment_id)

    if comment.content_object.permission_to(
            'manage', request.course, request.user):
        comment.comment = request.POST['comment']
    elif comment.user == request.user:
        now = datetime.now()
        comment.comment = '<div class="postupdate">[Post updated at \
            <time datetime="%s">%s</time>]</div>%s' % \
            (now.isoformat(),
             now.strftime('%I:%M%p %D').lower(),
             request.POST['comment'])
    else:
        return HttpResponseForbidden('You do not have permission \
                                     to edit this discussion.')

    if request.POST.get('title', None):
        comment.title = request.POST['title']
        if not comment.parent:
            disc_sc = comment.content_object
            disc_sc.title = comment.title
            disc_sc.save()

    comment.save()

    DiscussionIndex.update_class_references(comment.comment, comment.user,
                                            comment, comment.content_object,
                                            comment.user)

    if request.META['HTTP_ACCEPT'].startswith("text/html"):
        return {'comment': comment}
    else:
        ctx = {'context': threaded_comment_json(request, comment)}
        return HttpResponse(json.dumps(ctx), content_type='application/json')


def threaded_comment_citations(all_comments, viewer):
    """
    citation references to sherdnotes
    """
    citations = []
    from mediathread.djangosherd.models import SherdNote
    for obj in all_comments:
        refs = SherdNote.objects.references_in_string(obj.comment, viewer)
        citations.extend(refs)
    return citations


def threaded_comment_json(request, comment):
    viewer = request.user
    coll = ContentType.objects.get_for_model(Collaboration)
    all_comments = ThreadedComment.objects.filter(
        content_type=coll, object_pk=comment.content_object.pk,
        site__pk=settings.SITE_ID)
    all_comments = fill_tree(all_comments)
    all_comments = list(annotate_tree_properties(all_comments))

    rand = ''.join([choice(ascii_letters) for i in range(5)])  # nosec
    citations = threaded_comment_citations(all_comments, viewer)

    asset_resource = AssetResource()
    sherd_resource = SherdNoteResource()

    return {
        'type': 'discussion',
        'form': smart_text(django_comments.get_form()(comment.content_object)),
        'editing': True,
        'can_edit': True,
        'discussion': {
            'id': comment.id,
            'max_length': COMMENT_MAX_LENGTH,
            'thread': [{'open': obj.open if hasattr(obj, "open") else None,
                        'close': [i for i in obj.close]
                        if hasattr(obj, "close") else None,
                        'id': obj.id,
                        'author': obj.name,
                        'author_username': obj.user.username,
                        'submit_date': pretty_date(obj.submit_date),
                        'title': obj.title,
                        'content': obj.comment,
                        'can_edit': True if obj.user == viewer else False}
                       for obj in all_comments]
        },
        'assets': dict([('%s_%s' % (rand, ann.asset.pk),
                        asset_resource.render_one(request, ann.asset))
                        for ann in citations
                        if (ann.title != "Annotation Deleted" and
                            ann.title != 'Asset Deleted')]),
        'annotations': [sherd_resource.render_one(request, ann, rand)
                        for ann in citations],
    }
