from turtle import title
from django.db import models
from django.core.validators import URLValidator


class FeedSource(models.Model):
    '''
    Torrent feed source.
    '''
    title = models.CharField(max_length=255)
    url = models.URLField()

    def __str__(self) -> str:
        return self.title


class Torrent(models.Model):
    '''
    Torrent.
    '''
    guid = models.CharField(primary_key=True, max_length=40)
    title = models.CharField(max_length=255)
    pub_date = models.DateTimeField()
    link = models.URLField()
    enclosure_type = models.CharField(max_length=255)
    enclosure_length = models.PositiveBigIntegerField()
    enclosure_url = models.URLField(
        validators=[URLValidator(schemes=['http', 'https', 'ftp', 'ftps', 'magnet'])]
    )
    source = models.ForeignKey(FeedSource, on_delete=models.CASCADE, blank=True, null=True)
    added = models.BooleanField(default=False)
    alive = models.BooleanField(default=True)

    def __str__(self) -> str:
        return self.title


class FeedMatcher(models.Model):
    '''
    Torrent title matcher.
    '''
    pattern = models.CharField(max_length=255)
    download_dir = models.CharField(max_length=255)
    source = models.ForeignKey(FeedSource, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return self.pattern
