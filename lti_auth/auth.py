from hashlib import sha1
from courseaffils.models import Course
from django.contrib.auth.models import User, Group
from pylti.common import LTIException

from lti_auth.lti import LTI
from nameparser import HumanName


class LTIBackend(object):

    def create_user(self, lti, username):
        # create the user if necessary
        user = User(username=username, password='LTI user')
        user.set_unusable_password()
        user.email = lti.user_email()

        name = HumanName(lti.user_fullname())
        user.first_name = name.first[:30]
        user.last_name = name.last[:30]

        user.save()
        return user

    def get_hashed_username(self, lti):
            # (http://developers.imsglobal.org/userid.html)
        # generate a username to avoid overlap with existing system usernames
        # sha1 hash result + trunc to 30 chars should result in a valid
        # username with low-ish-chance of collisions
        uid = lti.consumer_user_id()
        return sha1(uid).hexdigest()[:30]

    def find_or_create_user(self, lti):
        # find the user via email address
        user = User.objects.filter(email=lti.user_email()).first()
        if user is None:
            username = self.get_hashed_username(lti)
            try:
                # find the user via generated lti user id
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                # finally, create a new lti user
                user = self.create_user(lti, username)

        return user

    def join_course(self, lti, course, user):
        # add the user to the requested course
        user.groups.add(course.group)
        for role in lti.user_roles():
            if role.lower() in ['staff', 'instructor', 'administrator']:
                user.groups.add(course.faculty_group)
                break

    def authenticate(self, request=None, request_type=None, role_type=None):
        if not request or not request_type or not role_type:
            return None

        try:
            lti = LTI(request_type, role_type)
            lti.verify(request)

            # validate course first
            try:
                coursename = lti.course_group()
                group = Group.objects.get(name=coursename)
                course = group.course
            except (Course.DoesNotExist, Group.DoesNotExist):
                lti.clear_session(request)
                return None

            user = self.find_or_create_user(lti)

            self.join_course(lti, course, user)

            return user

        except LTIException:
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
