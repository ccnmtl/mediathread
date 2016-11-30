from rest_framework import viewsets, permissions
from mediathread.sequence.models import (
    SequenceAsset, SequenceMediaElement, SequenceTextElement,
)
from mediathread.sequence.permissions import SingleAuthor, ReadOnly
from mediathread.sequence.serializers import (
    SequenceAssetSerializer, SequenceMediaElementSerializer,
    SequenceTextElementSerializer,
)


class SequenceAssetViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, SingleAuthor,)
    queryset = SequenceAsset.objects.all()
    serializer_class = SequenceAssetSerializer


class SequenceMediaElementViewSet(viewsets.ModelViewSet):
    permission_classes = (ReadOnly,)
    queryset = SequenceMediaElement.objects.all()
    serializer_class = SequenceMediaElementSerializer


class SequenceTextElementViewSet(viewsets.ModelViewSet):
    permission_classes = (ReadOnly,)
    queryset = SequenceTextElement.objects.all()
    serializer_class = SequenceTextElementSerializer
