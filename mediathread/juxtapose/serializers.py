from rest_framework import serializers
from mediathread.juxtapose.models import (
    JuxtaposeAsset, JuxtaposeMediaElement, JuxtaposeTextElement,
)


class JuxtaposeAssetSerializer(serializers.ModelSerializer):
    class Meta:
        model = JuxtaposeAsset
        fields = ('id', 'title', 'spine', 'course',
                  'juxtaposemediaelement_set',
                  'juxtaposetextelement_set',)

    spine = serializers.StringRelatedField()
    juxtaposemediaelement_set = serializers.HyperlinkedRelatedField(
        many=True, read_only=True, view_name='juxtaposemediaelement-detail')
    juxtaposetextelement_set = serializers.HyperlinkedRelatedField(
        many=True, read_only=True, view_name='juxtaposetextelement-detail')


class JuxtaposeMediaElementSerializer(serializers.ModelSerializer):
    class Meta:
        model = JuxtaposeMediaElement
        fields = ('id', 'media',)

    media = serializers.StringRelatedField()


class JuxtaposeTextElementSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = JuxtaposeTextElement
        fields = ('id', 'text',)
