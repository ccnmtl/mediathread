from djangosherd.models import SherdNote
from mediathread.api import ClassLevelAuthentication
from projects.models import Project
from tastypie import fields
from tastypie.authorization import Authorization
from tastypie.resources import ModelResource


class ProjectAuthorization(Authorization):
    def apply_limits(self, request, object_list, course=None):
        # HACK: Tastypie does not call apply_limits on m2m relationships
        # Course is calling apply_limits manually + specifying its course
        if course is None:
            course = request.course
        elif not course.is_member(request.user):
            return SherdNote.objects.none()

        # filter by course
        object_list = object_list.filter(course=course)

        # Filter projects to those visible by the requesting user
        # This is hackish...but the data structures are crazy complicated
        # @todo - refactor
        invisible = []
        for project in object_list:
            if not project.can_read(request):
                invisible.append(project.id)

        object_list = object_list.exclude(id__in=invisible)
        return object_list


class ProjectResource(ModelResource):

    # By default, all citations within a visible project are also visible
    selections = fields.ToManyField(
        'djangosherd.api.SherdNoteResource',
        blank=True, null=True, full=True,
        attribute=lambda bundle:
        SherdNote.objects.filter(
            pk__in=[c.id for c in bundle.obj.citations()]).order_by('id'))

    class Meta:
        queryset = Project.objects.all().order_by('id')
        excludes = ['author', 'participants', 'body', 'submitted', 'feedback']
        list_allowed_methods = ['get']
        detail_allowed_methods = ['get']
        authentication = ClassLevelAuthentication()
        authorization = ProjectAuthorization()

    def dehydrate(self, bundle):
        bundle.data['is_assignment'] = \
            bundle.obj.visibility_short() == 'Assignment'
        bundle.data['is_response'] = bundle.obj.assignment() is not None
        bundle.data['attribution'] = bundle.obj.attribution()
        return bundle
