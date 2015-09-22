from django.conf import settings
from django.http.response import HttpResponseServerError
from pylti.common import (
    LTIException, LTINotInSessionException, LTI_SESSION_KEY,
    LTI_ROLES, verify_request_common, LTI_PROPERTY_LIST)
from requests.sessions import session


class LTI(object):
    """
    LTI Object represents abstraction of current LTI session. It provides
    callback methods and methods that allow developer to inspect
    LTI basic-launch-request.

    This object is instantiated by @lti wrapper.
    """

    def __init__(self, request_type, role_type):
        self.request_type = request_type
        self.role_type = role_type
        self.nickname = self.name

    def name(self):  # pylint: disable=no-self-use
        """
        Name returns user's name or user's email or user_id
        :return: best guess of name to use to greet user
        """
        if 'lis_person_sourcedid' in session:
            return session['lis_person_sourcedid']
        elif 'lis_person_contact_email_primary' in session:
            return session['lis_person_contact_email_primary']
        elif 'user_id' in session:
            return session['user_id']
        else:
            return ''

    @property
    def user_id(self):  # pylint: disable=no-self-use
        """
        Returns user_id as provided by LTI

        :return: user_id
        """
        return session['user_id']

    def verify(self, request):
        """
        Verify if LTI request is valid, validation
        depends on @lti wrapper arguments

        :raises: LTIException
        """
        if self.request_type == 'session':
            self._verify_session(request)
        elif self.request_type == 'initial':
            self.verify_request(request)
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
            self.verify_request(request)

    @staticmethod
    def _verify_session(request):
        """
        Verify that session was already created

        :raises: LTIException
        """
        if not session.get(LTI_SESSION_KEY, False):
            raise LTINotInSessionException('Session expired or unavailable')

    def _consumers(self):
        """
        Gets consumer's map from config
        :return: consumers map
        """
        config = getattr(settings, 'PYLTI_CONFIG', dict())
        consumers = config.get('consumers', dict())
        return consumers

    @property
    def key(self):  # pylint: disable=no-self-use
        """
        OAuth Consumer Key
        :return: key
        """
        return session['oauth_consumer_key']

    @staticmethod
    def message_identifier_id():
        """
        Message identifier to use for XML callback

        :return: non-empty string
        """
        return "edX_fix"

    @property
    def lis_result_sourcedid(self):  # pylint: disable=no-self-use
        """
        lis_result_sourcedid to use for XML callback

        :return: LTI lis_result_sourcedid
        """
        return session['lis_result_sourcedid']

    @property
    def role(self):  # pylint: disable=no-self-use
        """
        LTI roles

        :return: roles
        """
        return session.get('roles')

    @staticmethod
    def is_role(role):
        """
        Verify if user is in role

        :param: role: role to verify against
        :return: if user is in role
        :exception: LTIException if role is unknown
        """
        roles = session['roles'].split(',')
        if role in LTI_ROLES:
            role_list = LTI_ROLES[role]
            # find the intersection of the roles
            roles = set(role_list) & set(roles)
            is_user_role_there = len(roles) >= 1
            return is_user_role_there
        else:
            raise LTIException("Unknown role {}.".format(role))

    def _check_role(self):
        """
        Check that user is in role specified as wrapper attribute

        :exception: LTIException if user is not in roles
        """
        return self.role_type

    @property
    def response_url(self):
        """
        Returns remapped lis_outcome_service_url
        uses PYLTI_URL_FIX map to support edX dev-stack

        :return: remapped lis_outcome_service_url
        """
        url = session['lis_outcome_service_url']
        urls = settings.get('PYLTI_URL_FIX', dict())
        # url remapping is useful for using devstack
        # devstack reports httpS://localhost:8000/ and listens on HTTP
        for prefix, mapping in urls.iteritems():
            if url.startswith(prefix):
                for _from, _to in mapping.iteritems():
                    url = url.replace(_from, _to)
        return url

    def verify_request(self, request):
        """
        Verify LTI request

        :raises: LTIException is request validation failed
        """
        if request.method == 'POST':
            params = dict(request.POST._iteritems())
        else:
            params = request.GET

        try:
            verify_request_common(self._consumers(),
                                  request.build_absolute_uri(),
                                  request.method, request.META,
                                  params)

            # All good to go, store all of the LTI params into a
            # session dict for use in views
            for prop in LTI_PROPERTY_LIST:
                if params.get(prop, None):
                    request.session[prop] = params[prop]

            # Set logged in session key
            request.session[LTI_SESSION_KEY] = True
            return True
        except LTIException:
            for prop in LTI_PROPERTY_LIST:
                if request.session.get(prop, None):
                    del request.session[prop]

            request.session[LTI_SESSION_KEY] = False
            raise

    @staticmethod
    def close_session():
        """
        Invalidates session
        """
        for prop in LTI_PROPERTY_LIST:
            if session.get(prop, None):
                del session[prop]
        session[LTI_SESSION_KEY] = False


class LTIMixin(object):
    role_type = 'any'
    request_type = 'any'

    def dispatch(self, *args, **kwargs):
        try:
            the_lti = LTI(self.request_type, self.role_type)
            the_lti.verify(self.request)
            the_lti._check_role()  # pylint: disable=protected-access
            kwargs['lti'] = the_lti
            return super(LTIMixin, self).dispatch(*args, **kwargs)
        except LTIException as lti_exception:
            return HttpResponseServerError(
                'An LTI error has occurred', str(lti_exception))


class lti(object):
    """
    LTI decorator

    :param: request - Request type from
        :py:attr:`pylti.common.LTI_REQUEST_TYPE`. (default: any)
    :param: roles - LTI Role (default: any)
    :return: wrapper
    """

    def __init__(self, request_type, role_type=u'any'):
        self.request_type = request_type
        self.role_type = role_type

    def __call__(self, func):
        def lti_func(view, *args, **kwargs):
            """
            Pass LTI reference to function or return error.
            """
            try:
                the_lti = LTI(self.request_type, self.role_type)
                the_lti.verify(view.request)
                the_lti._check_role()  # pylint: disable=protected-access
                # kwargs['lti'] = the_lti
                return func(view.request, *args, **kwargs)
            except LTIException as lti_exception:
                return HttpResponseServerError(
                    'An LTI error has occurred', str(lti_exception))

        lti_func.__name__ = func.__name__
        return lti_func
