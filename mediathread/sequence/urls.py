from django.urls import include, path
from rest_framework import routers
from mediathread.sequence.apiviews import (
    SequenceAssetViewSet, SequenceMediaElementViewSet,
    SequenceTextElementViewSet,
)


router = routers.DefaultRouter()
router.register(r'assets', SequenceAssetViewSet)
router.register(r'mediaelements', SequenceMediaElementViewSet)
router.register(r'textelements', SequenceTextElementViewSet)


urlpatterns = [
    path('api/', include(router.urls)),
]
