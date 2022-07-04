import re
import logging
from django.shortcuts import get_object_or_404, redirect, render
from django.http.request import HttpRequest
from django.db.models.query import QuerySet
from transmission_rpc import Client
from transrss.settings import TRANSMISSION_CONFIG
from transrss_manager.models import FeedSource, FeedMatcher, Torrent


def index(request: HttpRequest):
    feeds = FeedSource.objects.all()
    torrents = Torrent.objects.all()
    return render(request, "index.html", {
        'feeds': feeds,
        'torrents': torrents
    })


def feed_detail(request: HttpRequest, id: int):
    feed = get_object_or_404(FeedSource, pk=id)
    return render(request, 'feed.html', {
        'feed': feed,
        'feeds': FeedSource.objects.all(),
        'matchers': FeedMatcher.objects.filter(source=feed).all()
    })


def match_download(request: HttpRequest):
    """Match torrents and add to transmission

    Parameters
    ----------
    request : HttpRequest
        Http request instance.
    """
    client = Client(**TRANSMISSION_CONFIG)
    feeds = FeedSource.objects.all()
    for feed in feeds:
        torrents: QuerySet[Torrent] = Torrent.objects.filter(source=feed)
        matchers: QuerySet[FeedMatcher] = FeedMatcher.objects.filter(source=feed)
        for torrent in torrents:
            if torrent.added:
                continue
            for matcher in matchers:
                if re.search(matcher.pattern, torrent.title) is not None:
                    try:
                        client.add_torrent(torrent.enclosure_url, download_dir=matcher.download_dir, paused=True)
                        torrent.added = True
                    except Exception:
                        logging.error("Failed to add torrent '%s'.", torrent.title)
            torrent.save()
    return redirect(to="/")
