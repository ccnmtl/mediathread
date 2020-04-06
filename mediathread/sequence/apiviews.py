from rest_framework import viewsets, permissions
from mediathread.sequence.models import (
    SequenceAsset, SequenceMediaElement, SequenceTextElement,
)
from mediathread.sequence.permissions import SingleAuthor, ReadOnly
from mediathread.sequence.serializers import (
    SequenceAssetSerializer, SequenceMediaElementSerializer,
    SequenceTextElementSerializer,
)
from rest_framework.authentication import (
    SessionAuthentication, BasicAuthentication
)


# Mediathread doesn't have CsrfViewMiddleware in its MIDDLEWARE
# settings, unfortunately. Exempt csrf from ajax calls until that's
# enabled.
class CsrfExemptSessionAuthentication(SessionAuthentication):
    # https://stackoverflow.com/a/30875830/173630
    def enforce_csrf(self, request):
        return


class SequenceAssetViewSet(viewsets.ModelViewSet):
    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)
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
