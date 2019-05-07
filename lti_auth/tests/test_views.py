from django.test.testcases import TestCase
from pylti.common import LTI_SESSION_KEY

from lti_auth.lti import LTI
from lti_auth.tests.factories import LTICourseContextFactory, UserFactory, \
    CONSUMERS, generate_lti_request, BASE_LTI_PARAMS
from lti_auth.views import LTIAuthMixin, LTIRoutingView


class LTIViewTest(TestCase):

    def setUp(self):
        self.lti = LTI('initial', 'any')
        self.lti.lti_params = BASE_LTI_PARAMS.copy()

    def test_join_groups(self):
        mixin = LTIAuthMixin()
        ctx = LTICourseContextFactory()
        user = UserFactory()

        mixin.join_groups(self.lti, ctx, user)
        self.assertTrue(user in ctx.group.user_set.all())
        self.assertTrue(user in ctx.faculty_group.user_set.all())

    def test_join_groups_student(self):
        mixin = LTIAuthMixin()
        ctx = LTICourseContextFactory()
        user = UserFactory()

        self.lti.lti_params['roles'] = u'Learner'

        mixin.join_groups(self.lti, ctx, user)
        self.assertTrue(user in ctx.group.user_set.all())
        self.assertFalse(user in ctx.faculty_group.user_set.all())

    def test_join_groups_teachingassistant(self):
        mixin = LTIAuthMixin()
        ctx = LTICourseContextFactory()
        user = UserFactory()

        self.lti.lti_params['roles'] = \
            u'urn:lti:role:ims/lis/TeachingAssistant'

        mixin.join_groups(self.lti, ctx, user)
        self.assertTrue(user in ctx.group.user_set.all())
        self.assertFalse(user in ctx.faculty_group.user_set.all())

        with self.settings(LTI_ELEVATE_TEACHINGASSISTANTS=['instructure.edu']):
            mixin.join_groups(self.lti, ctx, user)
            self.assertTrue(user in ctx.group.user_set.all())
            self.assertTrue(user in ctx.faculty_group.user_set.all())

    def test_launch_invalid_user(self):
        request = generate_lti_request()

        response = LTIRoutingView().dispatch(request)
        self.assertEquals(response.status_code, 200)

        self.assertTrue('Authentication Failed' in response.content)
        self.assertFalse(request.session[LTI_SESSION_KEY])

    def test_launch_invalid_course(self):
        with self.settings(PYLTI_CONFIG={'consumers': CONSUMERS}):
            request = generate_lti_request()

            response = LTIRoutingView().dispatch(request)
            self.assertEquals(response.status_code, 200)

            self.assertTrue('Course Configuration' in response.content)

    def test_launch(self):
        with self.settings(PYLTI_CONFIG={'consumers': CONSUMERS},
                           LTI_EXTRA_PARAMETERS=['lti_version']):
            ctx = LTICourseContextFactory()
            request = generate_lti_request(ctx)

            view = LTIRoutingView()
            view.request = request

            response = view.dispatch(request)
            self.assertEquals(response.status_code, 302)

            landing = '/lti/landing/{}/?lti_version=LTI-1p0&'
            self.assertEquals(
                response.url, landing.format(ctx.lms_course_context))

            self.assertIsNotNone(request.session[LTI_SESSION_KEY])
            user = request.user
            self.assertFalse(user.has_usable_password())
            self.assertEquals(user.email, 'foo@bar.com')
            self.assertEquals(user.get_full_name(), 'Foo Baz')
            self.assertTrue(user in ctx.group.user_set.all())
            self.assertTrue(user in ctx.faculty_group.user_set.all())

    def test_launch_custom_landing_page(self):
        with self.settings(PYLTI_CONFIG={'consumers': CONSUMERS},
                           LTI_EXTRA_PARAMETERS=['lti_version']):
            ctx = LTICourseContextFactory()
            request = generate_lti_request(ctx, 'canvas')

            view = LTIRoutingView()
            view.request = request

            response = view.dispatch(request)
            landing = 'http://testserver/lti/landing/{}/?lti_version=LTI-1p0&'
            self.assertEquals(response.status_code, 302)
            self.assertTrue(
                response.url,
                landing.format(ctx.lms_course_context))

            self.assertIsNotNone(request.session[LTI_SESSION_KEY])
            user = request.user
            self.assertFalse(user.has_usable_password())
            self.assertEquals(user.email, 'foo@bar.com')
            self.assertEquals(user.get_full_name(), 'Foo Baz')
            self.assertTrue(user in ctx.group.user_set.all())
            self.assertTrue(user in ctx.faculty_group.user_set.all())

    def test_embed(self):
        with self.settings(PYLTI_CONFIG={'consumers': CONSUMERS},
                           LTI_EXTRA_PARAMETERS=['lti_version']):
            ctx = LTICourseContextFactory()
            request = generate_lti_request(ctx, 'canvas', 'embed')

            view = LTIRoutingView()
            view.request = request

            response = view.dispatch(request)
            self.assertEquals(response.status_code, 302)
            self.assertEquals(
                response.url,
                'http://testserver/asset/embed/?return_url=/asset/'
                '&lti_version=LTI-1p0&')

            self.assertIsNotNone(request.session[LTI_SESSION_KEY])
            user = request.user
            self.assertFalse(user.has_usable_password())
            self.assertEquals(user.email, 'foo@bar.com')
            self.assertEquals(user.get_full_name(), 'Foo Baz')
            self.assertTrue(user in ctx.group.user_set.all())
            self.assertTrue(user in ctx.faculty_group.user_set.all())
