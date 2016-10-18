from rest_framework import viewsets
from mediathread.juxtapose.models import (
    JuxtaposeAsset, JuxtaposeMediaElement, JuxtaposeTextElement,
)
from mediathread.juxtapose.serializers import (
    JuxtaposeAssetSerializer, JuxtaposeMediaElementSerializer,
    JuxtaposeTextElementSerializer,
)


class JuxtaposeAssetViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = JuxtaposeAsset.objects.all()
    serializer_class = JuxtaposeAssetSerializer


class JuxtaposeMediaElementViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = JuxtaposeMediaElement.objects.all()
    serializer_class = JuxtaposeMediaElementSerializer


class JuxtaposeTextElementViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = JuxtaposeTextElement.objects.all()
    serializer_class = JuxtaposeTextElementSerializer
