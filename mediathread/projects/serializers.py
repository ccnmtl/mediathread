from rest_framework import serializers
from mediathread.projects.models import ProjectSequenceAsset


class ProjectSequenceAssetSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ProjectSequenceAsset
        fields = ('id', 'sequence_asset', 'project')
