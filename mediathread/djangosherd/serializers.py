from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from mediathread.assetmgr.serializers import AssetSerializer
from mediathread.djangosherd.models import SherdNote


class SherdNoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = SherdNote
        fields = ('id', 'asset', 'is_global_annotation',
                  'range1', 'range2', 'annotation_data')

    asset = AssetSerializer(read_only=True)

    def to_internal_value(self, data):
        if not isinstance(data, int):
            msg = 'Incorrect type. Expected an int, but got {}'.format(data)
            raise ValidationError(msg)

        try:
            return SherdNote.objects.get(id=data)
        except SherdNote.DoesNotExist:
            msg = 'No SherdNote instance found with id {}'.format(data)
            raise ValidationError(msg)
