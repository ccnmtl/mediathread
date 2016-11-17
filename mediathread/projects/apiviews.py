from rest_framework import viewsets, permissions
from rest_framework.response import Response
from mediathread.projects.models import ProjectSequenceAsset
from mediathread.projects.serializers import ProjectSequenceAssetSerializer


class ProjectSequenceAssetViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = ProjectSequenceAsset.objects.all()
    serializer_class = ProjectSequenceAssetSerializer

    def list(self, request):
        queryset = ProjectSequenceAsset.objects.filter(
            sequence_asset__author=request.user)

        project = request.query_params.get('project', None)
        if project is not None:
            queryset = queryset.filter(project__pk=project)

        serializer = ProjectSequenceAssetSerializer(queryset, many=True)
        return Response(serializer.data)
