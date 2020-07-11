from mediathread.main.course_details import cached_course_is_faculty, \
    cached_course_collaboration, cached_course_is_member


class CollaborationPolicy(object):
    """
    Base Collaboration Policy
    """
    def permission_to(self, collaboration, permission, course, user):
        rv = getattr(self, permission, lambda c, r, u: False)(collaboration,
                                                              course, user)
        return rv


class PublicEditorsAreOwners(CollaborationPolicy):
    """
    Implements a basic policy of people who can edit can also manage the group
    """
    def read(self, collaboration, course, user):
        return True

    def edit(self, collaboration, course, user):
        user = user
        if user == collaboration.user:
            return True
        if collaboration.group_id:
            return collaboration.group.user_set.filter(pk=user.pk).exists()

        return False

    manage = edit
    delete = edit


class PrivateEditorsAreOwners(PublicEditorsAreOwners):
    def read(self, collaboration, course, user):
        return (user.is_staff or self.edit(collaboration, course, user))


class PrivateStudentAndFaculty(CollaborationPolicy):
    def manage(self, coll, course, user):
        course_collaboration = cached_course_collaboration(course)
        return (coll.context == course_collaboration and
                course and cached_course_is_faculty(course, user))

    delete = manage

    def read(self, coll, course, user):
        course_collaboration = cached_course_collaboration(course)
        return (coll.context == course_collaboration and
                ((course and cached_course_is_faculty(course, user)) or
                 coll.user_id == user.id or
                 (coll.group_id and
                  user in coll.group.user_set.all())))

    edit = read


class InstructorShared(PrivateEditorsAreOwners):
    def read(self, coll, course, user):
        return (self.manage(coll, course, user) or
                cached_course_is_faculty(course, user))


class InstructorManaged(CollaborationPolicy):
    def manage(self, coll, course, user):
        course_collaboration = cached_course_collaboration(course)
        return (coll.context == course_collaboration and
                ((course and cached_course_is_faculty(course, user)) or
                 coll.user == user))
    delete = manage

    def read(self, coll, course, user):
        course_collaboration = cached_course_collaboration(course)
        return (coll.context == course_collaboration)

    edit = read


class CourseProtected(CollaborationPolicy):
    def manage(self, coll, course, user):
        course_collaboration = cached_course_collaboration(course)
        return (coll.context == course_collaboration and
                (coll.user == user or
                 (coll.group and
                  user in coll.group.user_set.all())))

    edit = manage
    delete = manage

    def read(self, coll, course, user):
        if not course:
            return False

        course_collaboration = cached_course_collaboration(course)
        return (coll.context == course_collaboration and
                cached_course_is_member(course, user))


# Used for discussions
class CourseCollaboration(CourseProtected):
    edit = CourseProtected.read
