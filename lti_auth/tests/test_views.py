from django.test.client import RequestFactory
from django.test.testcases import TestCase
from pylti.common import LTI_SESSION_KEY

from lti_auth.lti import LTI
from lti_auth.models import LTICourseContext
from lti_auth.tests.factories import LTICourseContextFactory, UserFactory, \
    CONSUMERS, generate_lti_request, BASE_LTI_PARAMS, GroupFactory
from lti_auth.views import LTIAuthMixin, LTIRoutingView, LTICourseEnableView


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
            self.assertFalse(request.session[LTI_SESSION_KEY])

    def test_launch(self):
        with self.settings(PYLTI_CONFIG={'consumers': CONSUMERS},
                           LTI_EXTRA_PARAMETERS=['lti_version']):
            ctx = LTICourseContextFactory(enable=True)
            request = generate_lti_request(ctx)

            view = LTIRoutingView()
            view.request = request

            response = view.dispatch(request)
            self.assertEquals(response.status_code, 302)
            self.assertEquals(
                response.url,
                '/?lti_version=LTI-1p0&'.format(ctx.uuid))

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
            ctx = LTICourseContextFactory(enable=True)
            request = generate_lti_request(ctx, 'canvas')

            view = LTIRoutingView()
            view.request = request

            response = view.dispatch(request)
            self.assertEquals(response.status_code, 302)
            self.assertTrue(
                response.url,
                'http://testserver/landing/?lti_version=LTI-1p0&')

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
            ctx = LTICourseContextFactory(enable=True)
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

    def test_enable(self):
        view = LTICourseEnableView()
        group = GroupFactory()
        faculty_group = GroupFactory()
        user = UserFactory()

        data = {
            'group': group.id,
            'faculty_group': faculty_group.id,
            'lti-enable': '1'
        }

        # enable the first time
        request = RequestFactory().post('/', data)
        request.user = user
        view.request = request

        response = view.dispatch(request)
        self.assertEquals(response.status_code, 302)
        ctx = LTICourseContext.objects.get(group=group,
                                           faculty_group=faculty_group)
        self.assertTrue(ctx.enable)

    def test_disable(self):
        view = LTICourseEnableView()
        ctx = LTICourseContextFactory(enable=True)
        user = UserFactory()

        data = {
            'group': ctx.group.id,
            'faculty_group': ctx.faculty_group.id,
            'lti-enable': '0'
        }

        # enable the first time
        request = RequestFactory().post('/', data)
        request.user = user
        view.request = request

        view.dispatch(request)
        ctx.refresh_from_db()
        self.assertFalse(ctx.enable)

    def test_reenable(self):
        view = LTICourseEnableView()
        ctx = LTICourseContextFactory()
        user = UserFactory()

        data = {
            'group': ctx.group.id,
            'faculty_group': ctx.faculty_group.id,
            'lti-enable': '1'
        }

        # enable the first time
        request = RequestFactory().post('/', data)
        request.user = user
        view.request = request

        view.dispatch(request)
        ctx.refresh_from_db()
        self.assertTrue(ctx.enable)
