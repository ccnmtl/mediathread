from django.conf import settings
from django.contrib.auth import authenticate, login
from django.core.urlresolvers import reverse
from django.http.response import HttpResponseRedirect, HttpResponseForbidden
from django.views.generic.base import View, TemplateView


class LTILoginView(View):
    request_type = 'initial'
    role_type = 'any'

    def post(self, request):
        """ validates the LTI oAuth signature ticket and logs the user in """

        user = authenticate(request=request,
                            request_type=self.request_type,
                            role_type=self.role_type)
        if user is None:
            return HttpResponseForbidden('unable to login through LTI')

        login(request, user)

        lti_landing_page = request.POST.get('custom_landing_page', False)
        if lti_landing_page:
            # Canvas does not support launching in a new window/tab
            # Provide a "launch in new tab" landing page
            url = reverse('lti-landing-page')
        else:
            url = '/'

        # navigate to the course or the switch course page
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
            settings.LTI_TOOL_CONFIGURATION['icon_url'])

        ctx = {
            'domain': domain,
            'launch_url': launch_url,
            'icon_url': icon_url,
            'title': settings.LTI_TOOL_CONFIGURATION['title'],
            'description': settings.LTI_TOOL_CONFIGURATION['description'],
            'tool_id': settings.LTI_TOOL_CONFIGURATION['tool_id'],
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
