from rest_framework import serializers
from mediathread.sequence.models import (
    SequenceAsset, SequenceMediaElement, SequenceTextElement,
)


class SequenceAssetSerializer(serializers.ModelSerializer):
    class Meta:
        model = SequenceAsset
        fields = ('id', 'spine', 'course',
                  'sequencemediaelement_set',
                  'sequencetextelement_set',)

    spine = serializers.StringRelatedField()
    sequencemediaelement_set = serializers.HyperlinkedRelatedField(
        many=True, read_only=True, view_name='sequencemediaelement-detail')
    sequencetextelement_set = serializers.HyperlinkedRelatedField(
        many=True, read_only=True, view_name='sequencetextelement-detail')


class SequenceMediaElementSerializer(serializers.ModelSerializer):
    class Meta:
        model = SequenceMediaElement
        fields = ('id', 'media',)

    media = serializers.StringRelatedField()


class SequenceTextElementSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = SequenceTextElement
        fields = ('id', 'text',)
