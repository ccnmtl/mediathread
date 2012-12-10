from assetmgr.api import AssetAuthorization
from courseaffils.models import Course, CourseInfo
from mediathread.api import ClassLevelAuthentication
from mediathread.api import GroupResource
from projects.api import ProjectAuthorization
from tastypie import fields
from tastypie.authorization import Authorization
from tastypie.resources import ModelResource


class CourseMemberAuthorization(Authorization):

    def apply_limits(self, request, object_list):
        # User must be a member of all courses in the request list
        for course in object_list:
            if not course.is_member(request.user):
                return Course.objects.none()

        return object_list


class CourseInfoResource(ModelResource):
    class Meta:
        queryset = CourseInfo.objects.none()
        resource_name = 'info'
        allowed_methods = ['get']
        excludes = ['days', 'endtime', 'starttime']


class CourseResource(ModelResource):
    faculty_group = fields.ForeignKey(GroupResource,
                                      'faculty_group',
                                      full=True)

    info = fields.ForeignKey(CourseInfoResource, 'info',
                             full=True, blank=True, null=True)

    # All viewable assets - paginated at 20
    project_set = fields.ToManyField(
        'projects.api.ProjectResource', blank=True, null=True, full=True,
        attribute=lambda bundle: ProjectAuthorization().apply_limits(
            bundle.request,
            bundle.obj.project_set.all(), bundle.obj).order_by('id'))

    # All viewable assets - paginated at 20
    item_set = fields.ToManyField(
        'assetmgr.api.AssetResource', blank=True, null=True, full=True,
        attribute=lambda bundle: AssetAuthorization().apply_limits(
            bundle.request,
            bundle.obj.asset_set.all(), bundle.obj).order_by('id'))

    class Meta:
        queryset = Course.objects.all()
        excludes = ['group']
        list_allowed_methods = []
        detail_allowed_methods = ['get']

        # User is logged into some course
        authentication = ClassLevelAuthentication()

        # User is a member of this course
        authorization = CourseMemberAuthorization()
