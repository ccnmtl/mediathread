from rest_framework import serializers
from mediathread.djangosherd.models import SherdNote
from mediathread.sequence.models import (
    SequenceAsset, SequenceMediaElement, SequenceTextElement,
)


class SequenceMediaElementSerializer(serializers.ModelSerializer):
    class Meta:
        model = SequenceMediaElement
        fields = ('id', 'media', 'juxtaposition', 'start_time', 'end_time')

    media = serializers.PrimaryKeyRelatedField(
        queryset=SherdNote.objects.all())


class SequenceTextElementSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = SequenceTextElement
        fields = ('id', 'text', 'juxtaposition', 'start_time', 'end_time')


class SequenceAssetSerializer(serializers.ModelSerializer):
    class Meta:
        model = SequenceAsset
        fields = ('id', 'spine', 'course',
                  'sequencemediaelement_set',
                  'sequencetextelement_set',)

    spine = serializers.PrimaryKeyRelatedField(
        queryset=SherdNote.objects.all(), allow_null=True)
    sequencemediaelement_set = SequenceMediaElementSerializer(
        many=True, read_only=True)
    sequencetextelement_set = SequenceTextElementSerializer(
        many=True, read_only=True)
