from rest_framework import viewsets, permissions
from mediathread.sequence.models import (
    SequenceAsset, SequenceMediaElement, SequenceTextElement,
)
from mediathread.sequence.serializers import (
    SequenceAssetSerializer, SequenceMediaElementSerializer,
    SequenceTextElementSerializer,
)


class SequenceAssetViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = SequenceAsset.objects.all()
    serializer_class = SequenceAssetSerializer


class SequenceMediaElementViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = SequenceMediaElement.objects.all()
    serializer_class = SequenceMediaElementSerializer


class SequenceTextElementViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = SequenceTextElement.objects.all()
    serializer_class = SequenceTextElementSerializer
