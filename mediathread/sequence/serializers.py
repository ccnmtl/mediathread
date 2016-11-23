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
    sequencemediaelement_set = SequenceMediaElementSerializer(many=True)
    sequencetextelement_set = SequenceTextElementSerializer(many=True)

    def create(self, validated_data):
        instance = SequenceAsset.objects.create(
            author=validated_data.get('author'),
            course=validated_data.get('course'),
            spine=validated_data.get('spine'))
        instance.full_clean()
        return instance

    def update(self, instance, validated_data):
        instance.spine = validated_data.get('spine')
        instance.save()
        return instance
