#!/usr/bin/env python

import datetime
import PyRSS2Gen

class ItunesRSS(PyRSS2Gen.RSS2):
    """This class adds the "itunes" extension (<itunes:image>, etc.)
    to the rss feed."""

    rss_attrs = {
        "xmlns:itunes": "http://www.itunes.com/dtds/podcast-1.0.dtd",
        "version": "2.0",
    }

    def publish_extensions(self, handler):
        # implement this method to embed the <itunes:*> elements
        # into the channel header.
        if self.image is not None and \
           isinstance(self.image, PyRSS2Gen.Image) and \
           self.image.url is not None:
            handler.startElement('itunes:image',  {'href': self.image.url})
            handler.endElement('itunes:image')

class RSSer():
    """
    Creates an RSS feed for a list of items. Items must have a title, url,
    media url, description, and date.
    """
    def __init__(self, author, title, description, url, image, items, media_type='audio'):
        self.author = author
        self.title = title
        self.description = description
        self.url = url
        self.image = image
        self.items = items
        self.media_type = media_type

    def create(self):
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

        image = PyRSS2Gen.Image(url=self.image,
                                title=self.author,
                                link=self.url)

        rss = ItunesRSS(
            title=self.title,
            link=self.url,
            description=self.description,
            lastBuildDate=datetime.datetime.now(),
            image=image,
            items=rss_items
        )

        return rss.to_xml()
