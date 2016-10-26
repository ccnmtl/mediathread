from rest_framework import viewsets
from mediathread.sequence.models import (
    SequenceAsset, SequenceMediaElement, SequenceTextElement,
)
from mediathread.sequence.serializers import (
    SequenceAssetSerializer, SequenceMediaElementSerializer,
    SequenceTextElementSerializer,
)


class SequenceAssetViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SequenceAsset.objects.all()
    serializer_class = SequenceAssetSerializer


class SequenceMediaElementViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SequenceMediaElement.objects.all()
    serializer_class = SequenceMediaElementSerializer


class SequenceTextElementViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SequenceTextElement.objects.all()
    serializer_class = SequenceTextElementSerializer
