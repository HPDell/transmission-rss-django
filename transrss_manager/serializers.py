from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers
from transrss_manager.models import FeedSource, Torrent


class FeedSourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeedSource
        fields = ['id', 'title', 'url']


class TorrentSerializer(serializers.Serializer):
    guid = serializers.CharField()
    title = serializers.CharField()
    pub_date = serializers.DateTimeField()
    link = serializers.URLField()
    enclosure_type = serializers.CharField()
    enclosure_length = serializers.IntegerField()
    enclosure_url = serializers.URLField()
    source = FeedSourceSerializer()
    added = serializers.BooleanField(required=False)

    def create(self, validated_data):
        feed_data = validated_data.pop('source')
        try:
            feed = FeedSource.objects.get(**feed_data)
            return Torrent.objects.create(source=feed, **validated_data)
        except ObjectDoesNotExist as e:
            raise e
    
    def update(self, instance, validated_data):
        feed_id = validated_data.pop('source', instance.source)
        try:
            feed = FeedSource.objects.get(pk=feed_id)
            instance.title = validated_data.get('title', instance.title)
            instance.pub_date = validated_data.get('pub_date', instance.pub_date)
            instance.link = validated_data.get('link', instance.link)
            instance.guid = validated_data.get('guid', instance.guid)
            instance.enclosure_type = validated_data.get('enclosure_type', instance.enclosure_type)
            instance.enclosure_length = validated_data.get('enclosure_length', instance.enclosure_length)
            instance.enclosure_url = validated_data.get('enclosure_url', instance.enclosure_url)
            instance.source = feed
            instance.save()
            return instance
        except Exception as e:
            raise e
