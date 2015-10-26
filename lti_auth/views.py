from django.conf import settings
from django.contrib.auth import authenticate, login
from django.core.urlresolvers import reverse
from django.http.response import HttpResponseRedirect, HttpResponseForbidden
from django.views.generic.base import View, TemplateView


class LTIAuthMixin(object):
    role_type = 'any'
    request_type = 'any'

    def dispatch(self, *args, **kwargs):
        """ validates the LTI oAuth signature ticket and logs the user in """
        user = authenticate(request=self.request,
                            request_type=self.request_type,
                            role_type=self.role_type)
        if user is None:
            return HttpResponseForbidden('unable to login through LTI')

        login(self.request, user)

        return super(LTIAuthMixin, self).dispatch(*args, **kwargs)


class LTIRoutingView(LTIAuthMixin, View):
    request_type = 'initial'
    role_type = 'any'

    def post(self, request):
        if request.POST.get('ext_content_intended_use', '') == 'embed':
            domain = self.request.get_host()
            url = '%s://%s/%s?return_url=%s' % (
                self.request.scheme, domain,
                settings.LTI_TOOL_CONFIGURATION['embed_url'],
                request.POST.get('launch_presentation_return_url'))
        elif len(request.POST.get('custom_landing_page', '')) > 0:
            # Canvas does not support launching in a new window/tab
            # Provide a "launch in new tab" landing page
            url = reverse('lti-landing-page')
        else:
            url = '/'

        return HttpResponseRedirect(url)


class LTIConfigView(TemplateView):
    template_name = 'lti_auth/config.xml'
    content_type = 'text/xml; charset=utf-8'

    def get_context_data(self, **kwargs):
        domain = self.request.get_host()
        launch_url = '%s://%s/%s' % (
            self.request.scheme, domain,
            settings.LTI_TOOL_CONFIGURATION['launch_url'])
        icon_url = '%s://%s/%s' % (
            self.request.scheme, domain,
            settings.LTI_TOOL_CONFIGURATION['embed_icon_url'])

        ctx = {
            'domain': domain,
            'launch_url': launch_url,
            'title': settings.LTI_TOOL_CONFIGURATION['title'],
            'description': settings.LTI_TOOL_CONFIGURATION['description'],
            'embed_icon_url': icon_url,
            'embed_tool_id': settings.LTI_TOOL_CONFIGURATION['embed_tool_id'],
        }
        return ctx


class LTILandingPage(TemplateView):
    template_name = 'lti_auth/landing_page.html'

    def get_context_data(self, **kwargs):
        domain = self.request.get_host()
        landing_url = '%s://%s/' % (self.request.scheme, domain)

        return {
            'landing_url': landing_url,
            'title': settings.LTI_TOOL_CONFIGURATION['title']
        }
