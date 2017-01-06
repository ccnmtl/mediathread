from rest_framework import serializers

from mediathread.assetmgr.serializers import AssetSerializer
from mediathread.djangosherd.models import SherdNote


class SherdNoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = SherdNote
        fields = ('id', 'asset', 'is_global_annotation',
                  'range1', 'range2', 'annotation_data')

    asset = AssetSerializer(read_only=True)
