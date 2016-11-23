from rest_framework import serializers
from mediathread.djangosherd.models import SherdNote
from mediathread.projects.models import Project, ProjectSequenceAsset
from mediathread.sequence.models import (
    SequenceAsset, SequenceMediaElement, SequenceTextElement,
)


class SequenceMediaElementSerializer(serializers.ModelSerializer):
    class Meta:
        model = SequenceMediaElement
        fields = ('id', 'media', 'juxtaposition', 'start_time', 'end_time')

    media = serializers.PrimaryKeyRelatedField(
        queryset=SherdNote.objects.all())


class SequenceTextElementSerializer(serializers.ModelSerializer):
    class Meta:
        model = SequenceTextElement
        fields = ('id', 'text', 'juxtaposition', 'start_time', 'end_time')


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
        fields = ('id', 'spine', 'author', 'course',
                  'project',
                  'sequencemediaelement_set',
                  'sequencetextelement_set',)

    author = serializers.HiddenField(default=serializers.CurrentUserDefault())
    project = serializers.HiddenField(default=CurrentProjectDefault())
    spine = serializers.PrimaryKeyRelatedField(
        queryset=SherdNote.objects.all(), allow_null=True)
    sequencemediaelement_set = SequenceMediaElementSerializer(many=True)
    sequencetextelement_set = SequenceTextElementSerializer(many=True)

    def validate(self, data):
        # Only one SequenceAsset should ever be created for a given
        # author / project.
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
        return instance

    def update(self, instance, validated_data):
        instance.spine = validated_data.get('spine')
        instance.save()
        return instance
