from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.http.response import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import View, TemplateView
from lti_auth.lti import LTI
from lti_auth.models import LTICourseContext


class LTIAuthMixin(object):
    role_type = 'any'
    request_type = 'any'

    def join_groups(self, lti, ctx, user):
        # add the user to the requested groups
        user.groups.add(ctx.group)
        for role in lti.user_roles():
            role = role.lower()
            if ('staff' in role or
                'instructor' in role or
                    'administrator' in role):
                user.groups.add(ctx.faculty_group)
                break

            domains = getattr(settings, 'LTI_ELEVATE_TEACHINGASSISTANTS', [])
            if 'teachingassistant' in role and lti.canvas_domain() in domains:
                user.groups.add(ctx.faculty_group)
                break

    def dispatch(self, request, *args, **kwargs):
        lti = LTI(self.request_type, self.role_type)

        # validate the user via oauth
        user = authenticate(request=request, lti=lti)
        if user is None:
            lti.clear_session(request)
            return render(request, 'lti_auth/fail_auth.html', {})

        # login
        login(request, user)

        # check if course is configured
        try:
            ctx = LTICourseContext.objects.get(
                lms_course_context=lti.course_context())
        except (KeyError, ValueError, LTICourseContext.DoesNotExist):
            return render(
                request,
                'lti_auth/fail_course_configuration.html',
                {
                    'is_instructor': lti.is_instructor(),
                    'is_administrator': lti.is_administrator(),
                    'user': user,
                    'lms_course': lti.course_context(),
                    'lms_course_title': lti.course_title(),
                    'sis_course_id': lti.sis_course_id(),
                    'domain': lti.canvas_domain()
                })

        # add user to the course
        self.join_groups(lti, ctx, user)
        self.lti = lti
        return super(LTIAuthMixin, self).dispatch(request, *args, **kwargs)


@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(xframe_options_exempt, name='dispatch')
class LTIRoutingView(LTIAuthMixin, View):
    request_type = 'initial'
    role_type = 'any'

    def add_extra_parameters(self, url):
        if not hasattr(settings, 'LTI_EXTRA_PARAMETERS'):
            return

        if '?' not in url:
            url += '?'
        else:
            url += '&'

        for key in settings.LTI_EXTRA_PARAMETERS:
            url += '{}={}&'.format(key, self.request.POST.get(key, ''))

        return url

    def post(self, request):
        if request.POST.get('ext_content_intended_use', '') == 'embed':
            domain = self.request.get_host()
            url = '%s://%s/%s?return_url=%s' % (
                self.request.scheme, domain,
                settings.LTI_TOOL_CONFIGURATION['embed_url'],
                request.POST.get('launch_presentation_return_url'))
        else:
            url = reverse('lti-landing-page', args=[self.lti.course_context()])

        url = self.add_extra_parameters(url)
        return HttpResponseRedirect(url)


class LTIConfigView(TemplateView):
    template_name = 'lti_auth/config.xml'
    content_type = 'text/xml; charset=utf-8'

    def get_context_data(self, **kwargs):
        domain = self.request.get_host()
        launch_url = '%s://%s/%s' % (
            self.request.scheme, domain,
            settings.LTI_TOOL_CONFIGURATION['launch_url'])

        ctx = {
            'domain': domain,
            'launch_url': launch_url,
            'title': settings.LTI_TOOL_CONFIGURATION['title'],
            'description': settings.LTI_TOOL_CONFIGURATION['description'],
            'embed_icon_url':
                settings.LTI_TOOL_CONFIGURATION['embed_icon_url'],
            'embed_tool_id': settings.LTI_TOOL_CONFIGURATION['embed_tool_id'],
        }
        return ctx


@method_decorator(xframe_options_exempt, name='dispatch')
class LTILandingPage(TemplateView):
    template_name = 'lti_auth/landing_page.html'

    def get_context_data(self, **kwargs):
        domain = self.request.get_host()
        url = settings.LTI_TOOL_CONFIGURATION['landing_url'].format(
            self.request.scheme, domain, kwargs.get('context'))

        return {
            'landing_url': url,
            'title': settings.LTI_TOOL_CONFIGURATION['title']
        }


@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(xframe_options_exempt, name='dispatch')
class LTICourseEnableView(View):

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(self.__class__, self).dispatch(request, *args, **kwargs)

    def post(self, *args, **kwargs):
        group_id = self.request.POST.get('group')
        faculty_group_id = self.request.POST.get('faculty_group')
        course_context = self.request.POST.get('lms_course')
        title = self.request.POST.get('lms_course_title')

        (ctx, created) = LTICourseContext.objects.get_or_create(
            group=get_object_or_404(Group, id=group_id),
            faculty_group=get_object_or_404(Group, id=faculty_group_id),
            lms_course_context=course_context)

        messages.add_message(
            self.request, messages.INFO,
            '<b>Success!</b> {} is connected to Mediathread.'.format(title))

        url = reverse('lti-landing-page', args=[course_context])
        return HttpResponseRedirect(url)
