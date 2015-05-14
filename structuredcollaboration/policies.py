
class CollaborationPolicy(object):
    """
    Base Collaboration Policy
    """
    def permission_to(self, collaboration, permission, request):
        rv = getattr(self, permission, lambda c, r: False)(collaboration,
                                                           request)
        return rv


class PublicEditorsAreOwners(CollaborationPolicy):
    """
    Implements a basic policy of people who can edit can also manage the group
    """
    def read(self, collaboration, request):
        return True

    def edit(self, collaboration, request):
        user = request.user
        if user.is_authenticated():
            if user == collaboration.user:
                return True
            if collaboration.group_id:
                qs = collaboration.group.user_set.filter(pk=user.pk)
                return len(qs) > 0
        return False

    manage = edit
    delete = edit


class PrivateEditorsAreOwners(PublicEditorsAreOwners):
    def read(self, collaboration, request):
        return (request.user.is_staff or self.edit(collaboration, request))


class PrivateStudentAndFaculty(CollaborationPolicy):
    def manage(self, coll, request):
        return (coll.context == request.collaboration_context and
                request.course and
                request.course.is_faculty(request.user))

    delete = manage

    def read(self, coll, request):
        return (coll.context == request.collaboration_context and
                ((request.course and
                  request.course.is_faculty(request.user)) or
                 coll.user_id == request.user.id or
                 (coll.group_id and
                  request.user in coll.group.user_set.all())))

    edit = read


class InstructorShared(PrivateEditorsAreOwners):
    def read(self, coll, request):
        return (self.manage(coll, request) or
                request.course.is_faculty(request.user))


class InstructorManaged(CollaborationPolicy):
    def manage(self, coll, request):
        return (coll.context == request.collaboration_context and
                ((request.course and
                  request.course.is_faculty(request.user)) or
                 coll.user == request.user))
    delete = manage

    def read(self, coll, request):
        return (coll.context == request.collaboration_context)

    edit = read


class CourseProtected(CollaborationPolicy):
    def manage(self, coll, request):
        return (coll.context == request.collaboration_context and
                (coll.user == request.user or
                 (coll.group and
                  request.user in coll.group.user_set.all())))

    edit = manage
    delete = manage

    def read(self, coll, request):
        return (getattr(request, 'course', None) and
                coll.context == getattr(
                request, 'collaboration_context', None) and
                request.course.is_member(request.user))


class CourseCollaboration(CourseProtected):
    edit = CourseProtected.read


class Assignment(CourseProtected):
    def manage(self, coll, request):
        return (coll.context == request.collaboration_context and
                ((request.course and
                  request.course.is_faculty(request.user)) or
                 coll.user == request.user)
                )
    delete = manage
    edit = manage

    def read(self, coll, request):
        return (request.course and coll.context ==
                request.collaboration_context)

    add_child = read
