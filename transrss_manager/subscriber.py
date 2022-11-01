import os
import json
import re
from datetime import datetime
from dataclasses import dataclass, field
from time import sleep
from typing import List
import logging
import urllib3
import urllib3.response as res
from xsdata.formats.dataclass.parsers import XmlParser
from xsdata.formats.dataclass.parsers.config import ParserConfig

API_BASE_URL = r'http://127.0.0.1:9092/rss'

logger = logging.getLogger("subscriber_logger")
logger.setLevel(level=logging.INFO)
logger_handler = logging.StreamHandler()
logger_handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s"))
logger.addHandler(logger_handler)

global http
http = urllib3.PoolManager(headers={
    'Content-Type': 'application/json'
}, retries=False)
xmlparser = XmlParser(ParserConfig(fail_on_unknown_properties=False))

DJANGO_CREDENTIAL = {
    'username': os.getenv('DJANGO_SUPERUSER_USERNAME', 'admin'),
    'password': os.getenv('DJANGO_SUPERUSER_PASSWORD', 'admin')
}

@dataclass
class FeedSource:
    id: int
    title: str
    url: str


@dataclass
class RSSTorrentEnclosure:
    type: str = field(metadata={'type': 'Attribute'})
    length: int = field(metadata={'type': 'Attribute'})
    url: str = field(metadata={'type': 'Attribute'})


@dataclass
class RSSTorrent:
    title: str = field(metadata={'type': 'Element'})
    description: str = field(metadata={'type': 'Element'})
    pub_date: str = field(metadata={'type': 'Element', 'name': 'pubDate'})
    link: str = field(metadata={'type': 'Element'})
    guid: str = field(metadata={'type': 'Element'})
    author: str = field(metadata={'type': 'Element'})
    enclosure: RSSTorrentEnclosure = field(metadata={'type': 'Element'})
    comments: str = field(metadata={'type': 'Element'})
    category: str = field(metadata={'type': 'Element'})


@dataclass
class RSSChannelImage:
    url: str = field(metadata={'type': 'Element'})
    title: str = field(metadata={'type': 'Element'})
    link: str = field(metadata={'type': 'Element'})
    height: int = field(metadata={'type': 'Element'})
    width: int = field(metadata={'type': 'Element'})
    description: str = field(metadata={'type': 'Element'})


@dataclass
class RSSChannel:
    title: str = field(metadata={'type': 'Element'})
    language: str = field(metadata={'type': 'Element'})
    description: str = field(metadata={'type': 'Element'})
    image: RSSChannelImage = field(metadata={'type': 'Element'})
    pub_date: str = field(metadata={'type': 'Element', 'name': 'pubDate'})
    generator: str = field(metadata={'type': 'Element'})
    link: str = field(metadata={'type': 'Element'})
    copyright: str = field(metadata={'type': 'Element'})
    item: List[RSSTorrent] = field(metadata={'type': 'Element'}, default_factory=list)


@dataclass
class RSS:
    channel: RSSChannel = field(metadata={'type': 'Element'})


def torrent_upload(torrent: RSSTorrent, feed: FeedSource):
    check_res: res.HTTPResponse = http.request('GET', f'{API_BASE_URL}/api/torrent/{torrent.guid}/')
    if check_res.status == 200:
        logger.debug("Torrent already exists: %s", torrent.title)
        alive_res: res.HTTPResponse = http.request('PUT', f'{API_BASE_URL}/api/torrent/keep-alive/{torrent.guid}/')
        if alive_res.status == 200:
            logger.debug("Keep torrent alive: %s", torrent.title)
        else:
            logger.error("Cannot make torrent alive: %s", torrent.title)
    else:
        upload_data = json.dumps({
            'guid': torrent.guid,
            'title': torrent.title,
            'pub_date': datetime.strptime(torrent.pub_date, "%a, %d %b %Y %H:%M:%S %z").strftime("%Y-%m-%dT%H:%M:%S"),
            'link': torrent.link,
            'enclosure_type': torrent.enclosure.type,
            'enclosure_length': torrent.enclosure.length,
            'enclosure_url': torrent.enclosure.url,
            'source': {
                'id': feed.id,
                'title': feed.title,
                'url': feed.url
            }
        }).encode('utf-8')
        upload_res: res.HTTPResponse = http.request('POST', f'{API_BASE_URL}/api/torrent/', body=upload_data)
        if upload_res.status == 201:
            logger.info("Saved torrent %s", torrent.title)
        else:
            logger.error("Error when saving torrent %s: %s", torrent.title, upload_res.data.decode())


def feed_parse(feed: FeedSource):
    rss_res: res.HTTPResponse = http.request('GET', feed.url)
    if rss_res.status == 200:
        rss_body = ''.join([x for x in rss_res.data.decode() if x.isprintable()])
        rss: RSS = xmlparser.from_string(rss_body, RSS)
        for item in rss.channel.item:
            logger.debug("Found torrent published at %s : %s", item.pub_date, item.title)
            torrent_upload(item, feed)


def api_login():
    global http
    http = urllib3.PoolManager(headers={
        'Content-Type': 'application/json'
    }, retries=False)
    auth_res: res.HTTPResponse = http.request('POST', f'{API_BASE_URL}/api-auth-token/', body=json.dumps(DJANGO_CREDENTIAL).encode('utf-8'))
    if auth_res.status == 200:
        token = json.loads(auth_res.data)['token']
        # http.headers['X-CSRFToken'] = csrftoken
        http = urllib3.PoolManager(headers={
            'Content-Type': 'application/json',
            'Authorization': f'Token {token}'
        }, retries=False)
    else:
        detail = json.loads(auth_res.data)['detail']
        raise ValueError(f"Cannot login with the priveded credential {json.dumps(DJANGO_CREDENTIAL)}: {detail}")


def feed_begin_update():
    begin_res: res.HTTPResponse = http.request('POST', f'{API_BASE_URL}/api/torrent/begin-update/', fields={})
    if begin_res.status == 200:
        logger.debug("Set alive to false for all torrents.")
    else:
        logger.error("Cannot set alive to false for all torrents.")
        raise RuntimeError("Cannot set alive to false for all torrents.")


def feed_end_update():
    begin_res: res.HTTPResponse = http.request('DELETE', f'{API_BASE_URL}/api/torrent/end-update/')
    if begin_res.status == 200:
        logger.debug("Removed all died torrents.")
    else:
        logger.error("Cannot remove all died torrents.")
        raise RuntimeError("Cannot remove all died torrents.")


def feed_load():
    logger.info("Start checking RSS feeds.")
    api_login()
    feed_begin_update()
    fs_res: res.HTTPResponse = http.request('GET', f'{API_BASE_URL}/api/feed/')
    if fs_res.status == 200:
        fs_list = json.loads(fs_res.data)
        for i, source in enumerate(fs_list):
            feed = FeedSource(**source)
            logger.info("Reading #%s feed '%s'", i, feed.title)
            feed_parse(feed)
            logger.info("Successfully load #%s feed '%s'", i, feed.title)
        feed_end_update()
        match_res: res.HTTPResponse = http.request('GET', f'{API_BASE_URL}/api/torrent/match/')
        if match_res.status == 200:
            logger.info("Successfully refresh all torrents.")
    else:
        detail = json.loads(fs_res.data)['detail']
        logger.error("Failed to fetch feed sources: %s.", detail)

if __name__ == '__main__':
    try:
        feed_load()
    except Exception as e:
        logger.error(e)
