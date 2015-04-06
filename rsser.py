#!/usr/bin/env python

import datetime
import PyRSS2Gen

class RSSer():
    """
    Creates an RSS feed for a list of items. Items must have a title, url,
    media url, description, and date.
    """
    def __init__(self, author, title, description, url, items, media_type='audio'):
        self.author = author
        self.title = title
        self.description = description
        self.url = url
        self.items = items
        self.media_type = media_type

    def create(self, file):
        rss_items = []

        for item in self.items:
            rss_items.append(PyRSS2Gen.RSSItem(
                title=item.title,
                link=item.url,
                description=item.description,
                guid=PyRSS2Gen.Guid(item.url, False),
                pubDate=item.date,
                enclosure=PyRSS2Gen.Enclosure(item.media_url,
                                              0,
                                              "audio/mpeg" if self.media_type == 'audio' else "video/mp4")
            ))

        rss = PyRSS2Gen.RSS2(
            title=self.title,
            link=self.url,
            description=self.description,
            lastBuildDate=datetime.datetime.now(),
            items=rss_items
        )

        rss.write_xml(file)
