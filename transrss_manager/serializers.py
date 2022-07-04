from rest_framework import serializers
from transrss_manager.models import FeedSource, Torrent


class FeedSourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeedSource
        fields = ['title', 'url']


class TorrentSerializer(serializers.Serializer):
    title = serializers.CharField()
    pub_date = serializers.DateTimeField()
    link = serializers.URLField()
    guid = serializers.CharField()
    enclosure_type = serializers.CharField()
    enclosure_length = serializers.IntegerField()
    enclosure_url = serializers.URLField()
    added = serializers.BooleanField(required=False)

    def create(self, validated_data):
        return Torrent.objects.create(**validated_data)
    
    def update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)
        instance.pub_date = validated_data.get('pub_date', instance.pub_date)
        instance.link = validated_data.get('link', instance.link)
        instance.guid = validated_data.get('guid', instance.guid)
        instance.enclosure_type = validated_data.get('enclosure_type', instance.enclosure_type)
        instance.enclosure_length = validated_data.get('enclosure_length', instance.enclosure_length)
        instance.enclosure_url = validated_data.get('enclosure_url', instance.enclosure_url)
        instance.save()
        return instance
