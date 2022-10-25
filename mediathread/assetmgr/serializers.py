from rest_framework import serializers
from rest_framework.fields import SerializerMethodField

from mediathread.assetmgr.models import Asset, Source


class SourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Source
        fields = ('width', 'height', 'url', 'label')

    url = SerializerMethodField()

    def get_url(self, source):
        return source.url_processed(None)


class AssetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Asset
        fields = ('id', 'title', 'primary_source', 'media_type', 'transcript')

    primary_source = SerializerMethodField()

    def get_primary_source(self, asset):
        source = Source.objects.get(asset=asset, primary=True)
        serializer = SourceSerializer(instance=source)
        return serializer.data
