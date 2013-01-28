from courseaffils.models import Course, CourseInfo
from mediathread.api import ClassLevelAuthentication
from mediathread.api import GroupResource, ToManyFieldEx
from tastypie import fields
from tastypie.authorization import Authorization
from tastypie.constants import ALL_WITH_RELATIONS
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

    project_set = ToManyFieldEx(
        'projects.api.ProjectResource',
        'project_set',
        blank=True, null=True, full=True)

    asset_set = ToManyFieldEx(
        'assetmgr.api.AssetResource',
        'asset_set',
        blank=True, null=True, full=True)

    class Meta:
        queryset = Course.objects.all()
        excludes = ['group']
        list_allowed_methods = []
        detail_allowed_methods = ['get']

        # User is logged into some course
        authentication = ClassLevelAuthentication()

        # User is a member of this course
        authorization = CourseMemberAuthorization()

        filtering = {
            'project_set': ALL_WITH_RELATIONS,
            'asset_set': ALL_WITH_RELATIONS
        }
