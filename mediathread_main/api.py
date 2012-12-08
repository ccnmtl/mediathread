from courseaffils.models import Course, CourseInfo
from mediathread.api import ClassLevelAuthentication, GroupResource
from projects.api import ProjectAuthorization
from tastypie import fields
from tastypie.authorization import Authorization
from tastypie.resources import ModelResource


class CourseInfoResource(ModelResource):
    class Meta:
        queryset = CourseInfo.objects.none()
        resource_name = 'info'
        allowed_methods = ['get']
        excludes = ['days', 'endtime', 'starttime']


class CourseAuthorization(Authorization):
    def is_authorized(self, request, object=None):
        return object and object.is_member(request.user)


class CourseResource(ModelResource):
    faculty_group = fields.ForeignKey(GroupResource,
                                      'faculty_group',
                                      full=True)

    info = fields.ForeignKey(CourseInfoResource, 'info',
                             full=True,
                             blank=True,
                             null=True)

    project_filter = lambda bundle: ProjectAuthorization().apply_limits(
        bundle.request, bundle.obj.project_set.all())

    project_set = fields.ToManyField('mediathread_main.api.ProjectResource',
                                     blank=True, null=True, full=True,
                                     attribute=project_filter)

    # item_filter = lambda bundle: Asset.objects.references(bundle.obj,
    #                                                      bundle.obj.faculty)
    # item_set = fields.ToManyField('mediathread_main.api.AssetResource',
    #                              blank=True, null=True, full=True,
    #                              attribute=item_filter)

    class Meta:
        queryset = Course.objects.all()
        excludes = ['group']
        allowed_methods = ['get']

        # User is logged into some course
        authentication = ClassLevelAuthentication()

        # User has access to the requested object
        authorization = CourseAuthorization()
