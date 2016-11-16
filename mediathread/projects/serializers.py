from rest_framework import serializers
from mediathread.projects.models import ProjectSequenceAsset
from mediathread.sequence.serializers import SequenceAssetSerializer


class ProjectSequenceAssetSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ProjectSequenceAsset
        fields = ('id', 'sequence_asset', 'project')

    project = serializers.PrimaryKeyRelatedField(read_only=True)
    sequence_asset = SequenceAssetSerializer()
