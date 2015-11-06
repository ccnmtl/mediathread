from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse, resolve
from django.http import HttpResponseForbidden, HttpResponseServerError
from django.shortcuts import get_object_or_404

from structuredcollaboration.models import Collaboration


# For PUBLISHED TO WORLD compositions
# @todo -- refactor this into the project space
# tree management (add/remove leaf)
# re-ordering
# DO NOT PROVIDE 'MOVE' (intended to be unoptimized)
def view_collab_by_obj(request, context_slug, obj_type, obj_id):
    context = get_object_or_404(Collaboration, slug=context_slug)
    request.collaboration_context = context
    collab = get_object_or_404(
        Collaboration,
        context=context,
        content_type=ContentType.objects.get(model=obj_type),
        object_pk=obj_id)
    return serve_collaboration(request, collab)


def serve_collaboration(request, collab):
    if not collab.permission_to('read', request.course, request.user):
        return HttpResponseForbidden("forbidden")

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
