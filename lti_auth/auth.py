from hashlib import sha1

from django.contrib.auth.models import User
from nameparser import HumanName
from pylti.common import LTIException


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

    def get_username(self, lti):
        username = lti.user_identifier()
        if not username:
            username = self.get_hashed_username(lti)
        return username

    def find_user(self, lti):
        # find the user via lms identifier first
        user = User.objects.filter(username=lti.user_identifier()).first()

        # find the user via email address, if it exists
        if user is None and lti.user_email():
            user = User.objects.filter(email=lti.user_email()).first()

        if user is None:
            # find the user via hashed username
            username = self.get_hashed_username(lti)
            user = User.objects.filter(username=username).first()

        return user

    def find_or_create_user(self, lti):
        user = self.find_user(lti)
        if user is None:
            username = self.get_username(lti)
            user = self.create_user(lti, username)

        return user

    def authenticate(self, request=None, lti=None):
        try:
            lti.verify(request)
            return self.find_or_create_user(lti)
        except LTIException:
            lti.clear_session(request)
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
