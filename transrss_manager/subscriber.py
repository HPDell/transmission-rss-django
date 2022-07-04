import json
from datetime import datetime
from dataclasses import dataclass, field
from typing import List
import logging
import urllib3
import urllib3.response as res
from xsdata.formats.dataclass.parsers import XmlParser
from xsdata.formats.dataclass.parsers.config import ParserConfig

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')

http = urllib3.PoolManager()
xmlparser = XmlParser(ParserConfig(fail_on_unknown_properties=False))

@dataclass
class FeedSource:
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


def torrent_upload(torrent: RSSTorrent):
    check_res: res.HTTPResponse = http.request('GET', f'http://127.0.0.1:8000/api/torrent/{torrent.guid}/')
    if check_res.status == 200:
        logging.debug("Torrent already exists: %s", torrent.title)
    else:
        upload_data = json.dumps({
            'guid': torrent.guid,
            'title': torrent.title,
            'pub_date': datetime.strptime(torrent.pub_date, "%a, %d %b %Y %H:%M:%S %z").strftime("%Y-%m-%dT%H:%M:%S"),
            'link': torrent.link,
            'enclosure_type': torrent.enclosure.type,
            'enclosure_length': torrent.enclosure.length,
            'enclosure_url': torrent.enclosure.url
        }).encode('utf-8')
        upload_res: res.HTTPResponse = http.request('POST', 'http://127.0.0.1:8000/api/torrent/', body=upload_data)
        if upload_res.status == 201:
            logging.info("Saved torrent %s", torrent.title)
        else:
            logging.error("Error when saving torrent %s: %s", torrent.title, upload_res.data.decode())


def feed_parse(feed_url: str):
    rss_res: res.HTTPResponse = http.request('GET', feed_url)
    if rss_res.status == 200:
        rss: RSS = xmlparser.from_bytes(rss_res.data, RSS)
        for item in rss.channel.item:
            logging.debug("Found torrent published at %s : %s", item.pub_date, item.title)
            torrent_upload(item)


def subscribe():
    fs_res: res.HTTPResponse = http.request('GET', 'http://127.0.0.1:8000/api/feed-source/')
    if fs_res.status == 200:
        fs_list = json.loads(fs_res.data)
        for i, source in enumerate(fs_list):
            fs = FeedSource(**source)
            logging.info("Reading #%s feed '%s'", i, fs.title)
            feed_parse(fs.url)
    else:
        logging.error("Failed to fetch feed sources.")


if __name__ == '__main__':
    subscribe()