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


class CoursePublicCollaboration(CourseCollaboration):

    def read(self):
        return True


class Assignment(CollaborationPolicy):
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


class PublicAssignment(Assignment):
    def read(self, coll, request):
        return (coll.context == request.collaboration_context)


class CollaborationPoliciesSingleton(object):
    # purposely setting it where it stays static on the instance
    registered_policies = dict()
    policy_options = dict()

    def register_policy(self, policy_class, policy_key, policy_title):
        assert(len(policy_key) < 512)
        self.registered_policies[policy_key] = policy_class()
        self.policy_options[policy_key] = policy_title

    def __iter__(self):
        return iter(self.policy_options.items())

CollaborationPolicies = CollaborationPoliciesSingleton()


CollaborationPolicies.register_policy(CollaborationPolicy,
                                      'forbidden',
                                      'Forbidden to everyone')
CollaborationPolicies.register_policy(PublicEditorsAreOwners,
                                      'PublicEditorsAreOwners',
                                      'Editors can manage the group, \
                                       Content is world-readable')
CollaborationPolicies.register_policy(PrivateEditorsAreOwners,
                                      'PrivateEditorsAreOwners',
                                      'User and group can view/edit/manage. \
                                      Staff can read')

CollaborationPolicies.register_policy(
    InstructorManaged,
    'InstructorManaged',
    'Instructors/Staff and user manage, Course members read')

CollaborationPolicies.register_policy(
    InstructorShared,
    'InstructorShared',
    'group/user manage/edit and instructors can view')

CollaborationPolicies.register_policy(
    PrivateStudentAndFaculty,
    'PrivateStudentAndFaculty',
    'Private between faculty and student')

CollaborationPolicies.register_policy(
    CourseProtected,
    'CourseProtected',
    'Protected to Course Members')

CollaborationPolicies.register_policy(CourseCollaboration,
                                      'CourseCollaboration',
                                      'Course Collaboration')

CollaborationPolicies.register_policy(CoursePublicCollaboration,
                                      'CoursePublicCollaboration',
                                      'Public Course Collaboration')

CollaborationPolicies.register_policy(
    Assignment,
    'Assignment',
    'Course assignment (instructors can manage/edit, '
    'course members can read/respond)')

CollaborationPolicies.register_policy(
    PublicAssignment,
    'PublicAssignment',
    'Public Assignment (instructors can manage/edit, '
    'course members can respond, world can see)')
