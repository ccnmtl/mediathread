from rest_framework import serializers
from mediathread.djangosherd.models import SherdNote
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
        fields = ('media', 'start_time', 'end_time')

    media = serializers.PrimaryKeyRelatedField(
        queryset=SherdNote.objects.all())


class SequenceTextElementSerializer(serializers.ModelSerializer):
    class Meta:
        model = SequenceTextElement
        fields = ('text', 'start_time', 'end_time')


class CurrentProjectDefault(object):
    """This is based on djangorestframework's CurrentUserDefault."""
    def set_context(self, serializer_field):
        pid = serializer_field.context['request'].data.get('project')
        if pid:
            pid = int(pid)
        self.project = pid

    def __call__(self):
        return self.project


class SequenceAssetSerializer(serializers.ModelSerializer):
    class Meta:
        model = SequenceAsset
        fields = ('spine', 'author', 'course',
                  'project', 'media_elements', 'text_elements',)

    author = serializers.PrimaryKeyRelatedField(
        read_only=True, default=serializers.CurrentUserDefault())
    project = serializers.HiddenField(default=CurrentProjectDefault())
    spine = serializers.PrimaryKeyRelatedField(
        queryset=SherdNote.objects.all(), allow_null=True)
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

        if data.get('project'):
            project = Project.objects.get(pk=data.get('project'))
            if ProjectSequenceAsset.objects.filter(
                    sequence_asset__author=data.get('author'),
                    project=project).exists():
                raise serializers.ValidationError(
                    'A SequenceAsset already exists for this project '
                    'and user.')

        return data

    def create(self, validated_data):
        instance = SequenceAsset.objects.create(
            author=validated_data.get('author'),
            course=validated_data.get('course'),
            spine=validated_data.get('spine'))
        instance.full_clean()

        # Create nested resources
        for track_data in validated_data.get('media_elements'):
            e = SequenceMediaElement(sequence_asset=instance, **track_data)
            e.save()
        for track_data in validated_data.get('text_elements'):
            e = SequenceTextElement(sequence_asset=instance, **track_data)
            e.save()

        return instance

    def update(self, instance, validated_data):
        instance.spine = validated_data.get('spine')
        instance.save()

        # Create nested resources
        SequenceMediaElement.objects.filter(sequence_asset=instance).delete()
        for track_data in validated_data.get('media_elements'):
            e = SequenceMediaElement(sequence_asset=instance, **track_data)
            e.save()

        SequenceTextElement.objects.filter(sequence_asset=instance).delete()
        for track_data in validated_data.get('text_elements'):
            e = SequenceTextElement(sequence_asset=instance, **track_data)
            e.save()

        return instance
