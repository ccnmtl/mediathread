from rest_framework import viewsets, permissions
from mediathread.projects.models import ProjectSequenceAsset
from mediathread.projects.serializers import ProjectSequenceAssetSerializer


class ProjectSequenceAssetViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = ProjectSequenceAsset.objects.all()
    serializer_class = ProjectSequenceAssetSerializer
