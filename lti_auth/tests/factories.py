try:
    from urllib.parse import parse_qs, urlparse, urlencode
except ImportError:
    from urllib import urlencode
    from urlparse import parse_qs, urlparse

from django.contrib.auth.models import User, Group, AnonymousUser
from django.contrib.sessions.middleware import SessionMiddleware
from django.test.client import RequestFactory
import factory
from factory.django import DjangoModelFactory
import oauthlib.oauth1
from oauthlib.oauth1.rfc5849 import CONTENT_TYPE_FORM_URLENCODED
import six

from lti_auth.models import LTICourseContext


BASE_LTI_PARAMS = {
    u'launch_presentation_return_url': u'/asset/',
    u'lis_person_contact_email_primary': u'foo@bar.com',
    u'lis_person_name_full': u'Foo Bar Baz',
    u'lis_result_sourcedid': u'course-v1%3AedX%2BDemoX%2BDemo_Course'
                             u':-724d6c2b5fcc4a17a26b9120a1d463aa:student',
    u'lti_message_type': u'basic-lti-launch-request',
    u'lti_version': u'LTI-1p0',
    u'roles':
        u'urn:lti:instrole:ims/lis/Instructor,urn:lti:instrole:ims/lis/Staff',
    u'resource_link_id': u'-724d6c2b5fcc4a17a26b9120a1d463aa',
    u'user_id': u'student',
    u'custom_canvas_api_domain': u'instructure.edu'
}

CONSUMERS = {
    '__consumer_key__': {'secret': '__lti_secret__'}
}


def generate_lti_request(course_context=None, provider=None, use=None):
    """
    This code generated valid LTI 1.0 basic-lti-launch-request request
    """
    client = oauthlib.oauth1.Client('__consumer_key__',
                                    client_secret='__lti_secret__',
                                    signature_method=oauthlib.oauth1.
                                    SIGNATURE_HMAC,
                                    signature_type=oauthlib.oauth1.
                                    SIGNATURE_TYPE_QUERY)

    params = BASE_LTI_PARAMS.copy()
    if course_context:
        params.update({'context_id': course_context.lms_course_context})
    if provider:
        params.update({'tool_consumer_info_product_family_code': provider})
    if use:
        params.update({'ext_content_intended_use': use})

    signature = client.sign(
        'http://testserver/lti/',
        http_method='POST', body=urlencode(params),
        headers={'Content-Type': CONTENT_TYPE_FORM_URLENCODED})

    url_parts = urlparse(signature[0])
    query_string = parse_qs(url_parts.query, keep_blank_values=True)
    verify_params = dict()
    for key, value in six.iteritems(query_string):
        verify_params[key] = value[0]

    params.update(verify_params)

    request = RequestFactory().post('/lti/', params)

    middleware = SessionMiddleware()
    middleware.process_request(request)
    request.session.save()

    request.user = AnonymousUser()
    return request


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User
    username = factory.Sequence(lambda n: 'user%d' % n)
    password = factory.PostGenerationMethodCall('set_password', 'test')


class GroupFactory(DjangoModelFactory):
    class Meta:
        model = Group
    name = factory.Sequence(lambda n: 'group %s' % n)


class LTICourseContextFactory(DjangoModelFactory):
    class Meta:
        model = LTICourseContext

    group = factory.SubFactory(GroupFactory)
    faculty_group = factory.SubFactory(GroupFactory)
    lms_course_context = factory.Sequence(lambda n: 'lti%d' % n)
