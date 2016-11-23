from rest_framework import viewsets, permissions
from django.shortcuts import get_object_or_404
from mediathread.projects.models import Project, ProjectSequenceAsset
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

    def perform_create(self, serializer):
        assignment_pid = serializer.context['request'].data.get('project')
        instance = serializer.save(
            author=self.request.user, project=assignment_pid)
        p = get_object_or_404(Project, pk=assignment_pid)
        ProjectSequenceAsset.objects.get_or_create(
            sequence_asset=instance, project=p)


class SequenceMediaElementViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = SequenceMediaElement.objects.all()
    serializer_class = SequenceMediaElementSerializer


class SequenceTextElementViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = SequenceTextElement.objects.all()
    serializer_class = SequenceTextElementSerializer
