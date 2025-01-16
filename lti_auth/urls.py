from django.urls import path

from lti_auth.views import LTIConfigView, LTILandingPage, LTIRoutingView, \
    LTICourseEnableView
from lti_tool.views import jwks, OIDCLoginInitView


urlpatterns = [
    path('config.xml', LTIConfigView.as_view(), {}, 'lti-config'),
    path('enable/', LTICourseEnableView.as_view(), {}, 'lti-enable-course'),
    path('landing/<slug:context>/',
         LTILandingPage.as_view(), {}, 'lti-landing-page'),
    path('', LTIRoutingView.as_view(), {}, 'lti-login'),

    # django-lti
    path('.well-known/jwks.json', jwks, name='jwks'),
    path('init/<uuid:registration_uuid>/',
         OIDCLoginInitView.as_view(), name='oidc_init'),
]
