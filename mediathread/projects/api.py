from courseaffils.models import Course
from django.contrib.contenttypes.models import ContentType
from mediathread.djangosherd.models import SherdNote
from mediathread.api import UserResource, ClassLevelAuthentication
from mediathread.projects.models import Project
from structuredcollaboration.models import Collaboration
from tastypie import fields
from tastypie.authorization import Authorization
from tastypie.constants import ALL_WITH_RELATIONS
from tastypie.resources import ModelResource


class ProjectAuthorization(Authorization):

    def apply_limits(self, request, object_list):
        # collaboration context for the parent course
        save_course = request.course
        save_context = request.collaboration_context

        invisible = []
        for project in object_list:
            # courseafills policies introspects the request object.
            # initialize one for the project
            policy_request = request
            if project.course != request.course:
                policy_request.course = project.course

                policy_request.collaboration_context = \
                    Collaboration.objects.get(
                        content_type=ContentType.objects.get_for_model(Course),
                        object_pk=str(project.course.pk))

            else:
                policy_request = request

            if not project.collaboration(policy_request).permission_to(
                    'read', policy_request):
                invisible.append(project.id)

            request.course = save_course
            request.collaboration_context = save_context

        object_list = object_list.exclude(id__in=invisible)
        return object_list.order_by('id')


class ProjectResource(ModelResource):

    author = fields.ForeignKey(UserResource, 'author', full=True)

    # By default, all citations within a visible project are also visible
    sherdnote_set = fields.ToManyField(
        'mediathread.djangosherd.api.SherdNoteResource',
        blank=True, null=True, full=True,
        attribute=lambda bundle:
        SherdNote.objects.filter(
            pk__in=[c.id for c in bundle.obj.citations()]).order_by('id'))

    class Meta:
        queryset = Project.objects.all().order_by('id')
        excludes = ['participants', 'body', 'submitted', 'feedback']
        list_allowed_methods = ['get']
        detail_allowed_methods = ['get']
        authentication = ClassLevelAuthentication()
        authorization = ProjectAuthorization()
        ordering = ['id', 'title']

        filtering = {
            'author': ALL_WITH_RELATIONS
        }

    def dehydrate(self, bundle):
        bundle.data['is_assignment'] = \
            bundle.obj.visibility_short() == 'Assignment'
        bundle.data['is_response'] = bundle.obj.assignment() is not None
        bundle.data['attribution'] = bundle.obj.attribution()
        bundle.data['annotations'] = bundle.data.pop('sherdnote_set')
        return bundle
