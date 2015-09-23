from django.contrib.auth import authenticate, login
from django.http.response import HttpResponseRedirect, HttpResponseForbidden
from django.views.generic.base import View


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

        # navigate to the course or the switch course page
        return HttpResponseRedirect('/')
