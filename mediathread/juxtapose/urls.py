from django.conf.urls import url, include
from rest_framework import routers
from mediathread.juxtapose.apiviews import (
    JuxtaposeAssetViewSet, JuxtaposeMediaElementViewSet,
    JuxtaposeTextElementViewSet,
)


router = routers.DefaultRouter()
router.register(r'assets', JuxtaposeAssetViewSet)
router.register(r'mediaelements', JuxtaposeMediaElementViewSet)
router.register(r'textelements', JuxtaposeTextElementViewSet)


urlpatterns = [
    url(r'^api/', include(router.urls)),
]
