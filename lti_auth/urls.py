from django.urls import path

from lti_auth.views import (
    LTIConfigView, LTILandingPage, LTIRoutingView,
    LTICourseEnableView,

    LTI1p3JSONConfigView, LTI1p3LaunchView, MyOIDCLoginInitView
)
from lti_tool.views import jwks


urlpatterns = [
    path('config.xml', LTIConfigView.as_view(), {}, 'lti-config'),
    path('enable/', LTICourseEnableView.as_view(), {}, 'lti-enable-course'),
    path('landing/<slug:context>/',
         LTILandingPage.as_view(), {}, 'lti-landing-page'),
    path('', LTIRoutingView.as_view(), {}, 'lti-login'),

    # django-lti
    path('.well-known/jwks.json', jwks, name='jwks'),
    path('init/<uuid:registration_uuid>/',
         MyOIDCLoginInitView.as_view(), name='oidc_init'),
    path('<uuid:registration_uuid>/config.json',
         LTI1p3JSONConfigView.as_view()),
    path('launch/', LTI1p3LaunchView.as_view(), name='lti-launch'),
]
