from django.conf import settings
from pylti.common import (
    LTIException, LTINotInSessionException, LTI_SESSION_KEY,
    verify_request_common, LTIRoleException, LTI_ROLES)

from lti_auth.models import LTICourseContext


class LTI(object):
    """
    LTI Object represents abstraction of current LTI session. It provides
    callback methods and methods that allow developer to inspect
    LTI basic-launch-request.

    This object is instantiated by the LTIMixin
    """

    def __init__(self, request_type, role_type):
        self.request_type = request_type
        self.role_type = role_type
        self.lti_params = {}

    def consumer_user_id(self):  # pylint: disable=no-self-use
        """
        Returns user_id as provided by LTI
        """
        return "%s-%s" % \
            (self.lti_params['oauth_consumer_key'],
             self.lti_params['user_id'])

    def user_identifier(self):
        if 'lis_person_sourcedid' in self.lti_params:
            return self.lti_params['lis_person_sourcedid']

    def user_email(self):
        """
        Returns user email as provided by LTI
        """
        if 'lis_person_contact_email_primary' in self.lti_params:
            return self.lti_params['lis_person_contact_email_primary']

        return None

    def user_fullname(self):
        """
        Returns user's full name as provided by LTI
        """
        if ('lis_person_name_full' in self.lti_params and
                len(self.lti_params['lis_person_name_full']) > 0):
            return self.lti_params['lis_person_name_full']

        if 'user_id' in self.lti_params:
            return self.lti_params['user_id']

        return ''

    def user_roles(self):  # pylint: disable=no-self-use
        """
        LTI roles of the authenticated user

        :return: roles
        """
        if 'roles' in self.lti_params:
            return self.lti_params.get('roles', None).split(',')

        return []

    def course_context(self):
        if 'context_id' in self.lti_params:
            return self.lti_params.get('context_id')

    def custom_course_context(self):
        """
        Returns the custom LTICourseContext id as provided by LTI

        throws: KeyError or ValueError or LTICourseContext.DoesNotExist
        :return: context -- the LTICourseContext instance or None
        """
        return LTICourseContext.objects.get(
            enable=True,
            uuid=self.lti_params['custom_course_context'])

    def clear_session(self, request):
        """
        Invalidate the session
        """
        if LTI_SESSION_KEY in request.session:
            request.session[LTI_SESSION_KEY] = False

    def verify(self, request):
        """
        Verify if LTI request is valid, validation
        depends on arguments

        :raises: LTIException
        """
        if self.request_type == 'session':
            self._verify_session(request)
        elif self.request_type == 'initial':
            self._verify_request(request)
        elif self.request_type == 'any':
            self._verify_any(request)
        else:
            raise LTIException("Unknown request type")

        return True

    def _verify_any(self, request):
        """
        Verify that request is in session or initial request

        :raises: LTIException
        """
        try:
            self._verify_session(request)
        except LTINotInSessionException:
            self._verify_request(request)

    @staticmethod
    def _verify_session(request):
        """
        Verify that session was already created

        :raises: LTIException
        """
        if not request.session.get(LTI_SESSION_KEY, False):
            raise LTINotInSessionException('Session expired or unavailable')

    def _verify_request(self, request):
        """
        Verify LTI request

        :raises: LTIException is request validation failed
        """
        if request.method == 'POST':
            params = dict(request.POST.iteritems())
        else:
            params = dict(request.GET.iteritems())

        try:
            verify_request_common(self._consumers(),
                                  request.build_absolute_uri(),
                                  request.method, request.META,
                                  params)

            self._validate_role()

            self.lti_params = params
            request.session[LTI_SESSION_KEY] = True
            return True
        except LTIException:
            self.lti_params = {}
            request.session[LTI_SESSION_KEY] = False
            raise

    def _consumers(self):
        """
        Gets consumer's map from config
        :return: consumers map
        """
        config = getattr(settings, 'PYLTI_CONFIG', dict())
        consumers = config.get('consumers', dict())
        return consumers

    def _validate_role(self):
        """
        Check that user is in accepted/specified role

        :exception: LTIException if user is not in roles
        """
        if self.role_type != u'any':
            if self.role_type in LTI_ROLES:
                role_list = LTI_ROLES[self.role_type]

                # find the intersection of the roles
                roles = set(role_list) & set(self.user_roles())
                if len(roles) < 1:
                    raise LTIRoleException('Not authorized.')
            else:
                raise LTIException("Unknown role {}.".format(self.role_type))

        return True
