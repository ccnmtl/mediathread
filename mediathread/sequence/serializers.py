from decimal import Decimal
from rest_framework import serializers

from mediathread.djangosherd.serializers import SherdNoteReadOnlySerializer
from mediathread.projects.models import Project, ProjectSequenceAsset
from mediathread.sequence.models import (
    SequenceAsset, SequenceMediaElement, SequenceTextElement,
)
from mediathread.sequence.validators import (
    prevent_overlap, valid_start_end_times
)


class SequenceMediaElementSerializer(serializers.ModelSerializer):
    class Meta:
        model = SequenceMediaElement
        fields = ('media', 'media_asset', 'start_time', 'end_time', 'volume')

    media = SherdNoteReadOnlySerializer()
    media_asset = serializers.ReadOnlyField(source='media.asset.id')

    def to_internal_value(self, data):
        try:
            data['start_time'] = Decimal(data['start_time']).quantize(
                Decimal('.00001'))
        except TypeError:
            data['start_time'] = None

        try:
            data['end_time'] = Decimal(data['end_time']).quantize(
                Decimal('.00001'))
        except TypeError:
            data['end_time'] = None

        return super(SequenceMediaElementSerializer, self).to_internal_value(
            data)


class SequenceTextElementSerializer(serializers.ModelSerializer):
    class Meta:
        model = SequenceTextElement
        fields = ('text', 'start_time', 'end_time')

    def to_internal_value(self, data):
        try:
            data['start_time'] = Decimal(data['start_time']).quantize(
                Decimal('.00001'))
        except TypeError:
            data['start_time'] = None

        try:
            data['end_time'] = Decimal(data['end_time']).quantize(
                Decimal('.00001'))
        except TypeError:
            data['end_time'] = None

        return super(SequenceTextElementSerializer, self).to_internal_value(
            data)


class CurrentProjectDefault(object):
    """This is based on djangorestframework's CurrentUserDefault."""
    requires_context = True

    def __call__(self, serializer_field):
        pid = serializer_field.context['request'].data.get('project')
        if pid:
            pid = int(pid)
        self.project = pid
        return self.project


class SequenceAssetSerializer(serializers.ModelSerializer):
    class Meta:
        model = SequenceAsset
        fields = ('id', 'spine', 'spine_asset', 'spine_volume',
                  'author', 'course', 'project', 'media_elements',
                  'text_elements',)

    author = serializers.PrimaryKeyRelatedField(
        read_only=True, default=serializers.CurrentUserDefault())
    project = serializers.HiddenField(default=CurrentProjectDefault())
    spine = SherdNoteReadOnlySerializer(required=False, allow_null=True)
    spine_asset = serializers.ReadOnlyField(source='spine.asset.id')
    media_elements = SequenceMediaElementSerializer(many=True)
    text_elements = SequenceTextElementSerializer(many=True)

    def validate(self, data):
        text_elements = data.get('text_elements')
        media_elements = data.get('media_elements')

        if not data.get('spine') and (
                len(text_elements) > 0 or len(media_elements) > 0):
            raise serializers.ValidationError(
                'A SequenceAsset with track elements and no spine is invalid.')

        valid_start_end_times(text_elements + media_elements)

        prevent_overlap(text_elements)
        prevent_overlap(media_elements)

        return data

    def create(self, validated_data):
        current_user = self.context.get('request').user

        project = Project.objects.get(pk=validated_data.get('project'))
        if ProjectSequenceAsset.objects.filter(
                sequence_asset__author=current_user,
                project=project).exists():
            raise serializers.ValidationError(
                'A SequenceAsset already exists for this project '
                'and user.')

        instance = SequenceAsset.objects.create(
            author=current_user,
            course=validated_data.get('course'),
            spine=validated_data.get('spine'),
            spine_volume=validated_data.get('spine_volume', 80))
        instance.full_clean()

        instance.update_track_elements(
            validated_data.get('media_elements'),
            validated_data.get('text_elements'))

        ProjectSequenceAsset.objects.get_or_create(
            sequence_asset=instance, project=project)

        return instance

    def update(self, instance, validated_data):
        instance.spine = validated_data.get('spine')
        instance.spine_volume = validated_data.get('spine_volume', 80)
        instance.save()

        instance.update_track_elements(
            validated_data.get('media_elements'),
            validated_data.get('text_elements'))

        return instance
