from structuredcollaboration.models import Collaboration
from django.http import HttpResponseForbidden, HttpResponseServerError
from django.http import HttpResponseNotFound, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse, resolve
from django.contrib.contenttypes.models import ContentType

# tree management (add/remove leaf)
# re-ordering
# DO NOT PROVIDE 'MOVE' (intended to be unoptimized)


def view_collab_by_obj(request, context_slug, obj_type, obj_id):
    context = get_object_or_404(Collaboration, slug=context_slug)
    request.collaboration_context = context
    collab = get_object_or_404(Collaboration,
                               context=context,
                               content_type=
                               ContentType.objects.get(model=obj_type),
                               object_pk=obj_id)
    return serve_collaboration(request, collab)


def view_collab_by_collab(request, context_slug, collab_id):
    context = get_object_or_404(Collaboration, slug=context_slug)
    request.collaboration_context = context
    collab = get_object_or_404(Collaboration,
                               context=context,
                               pk=collab_id)
    return serve_collaboration(request, collab)


def view_collab_by_slug(request, context_slug, collab_slug):
    context = get_object_or_404(Collaboration, slug=context_slug)
    request.collaboration_context = context
    collab = get_object_or_404(Collaboration,
                               context=context,
                               slug=collab_slug)
    return serve_collaboration(request, collab)


def serve_collaboration(request, collab):
    if not collab.permission_to('read', request):
        return HttpResponseForbidden("forbidden")

    # Method 1. obj.default_view(request,obj)
    if hasattr(collab.content_object, 'default_view'):
        return collab.content_object.default_view(request,
                                                  collab.content_object)
    elif callable(getattr(collab.content_object, 'instance', False)):
        # support for modelversioned versions (mondrian branch)
        versioned_object = collab.content_object.instance()
        if hasattr(versioned_object, 'default_view'):
            return versioned_object.default_view(request, versioned_object)

    # Method 2. reverse('{obj-type}-view',obj_id)
    possible_link = reverse('%s-view' % collab.content_type.model,
                            args=[collab.content_object.pk])

    if possible_link:
        view, args, kwargs = resolve(possible_link)
        kwargs['request'] = request
        if 'check_permission' in view.func_code.co_varnames:
            kwargs['check_permission'] = False
        return view(*args, **kwargs)

    return HttpResponseServerError('No method to view object %s/%s/%d' %
                                   (collab.pk,
                                    collab.content_type.model,
                                    collab.content_object.pk,))


def collaboration_dispatch(request, collab_id, next=None):
    if request.method == "DELETE":
        return delete_collaboration(request, collab_id, next)

    return HttpResponseNotFound


def delete_collaboration(request, collab_id, next=None):
    # only fake-delete it.  We move it out from the context
    disc_sc = get_object_or_404(Collaboration, pk=collab_id)
    if not disc_sc.permission_to('delete', request):
        return HttpResponseForbidden('You do not have permission \
                                     to delete this discussion.')

    disc_sc.context = None
    disc_sc.content_object = None
    disc_sc._parent = None
    disc_sc.save()

    return HttpResponseRedirect(next or "/")


def collaboration_rss(request, context_slug):
    "RSS feed for collaboration tree"
    pass
