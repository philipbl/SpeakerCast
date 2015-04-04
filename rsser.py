#!/usr/bin/env python

import datetime
import PyRSS2Gen

class RSSer():
    def __init__(self, speaker, title, description, url, talks, media_type='audio'):
        self.speaker = speaker
        self.title = title
        self.description = description
        self.url = url
        self.talks = talks
        self.media_type = media_type

    def create(self, file):
        items = []

        for talk in self.talks:
            items.append(PyRSS2Gen.RSSItem(
                title=talk.title,
                link=talk.url,
                description=talk.description,
                guid=PyRSS2Gen.Guid(talk.url, False),
                pubDate=talk.date,
                enclosure=PyRSS2Gen.Enclosure(talk.media_url,
                                              0,
                                              "audio/mpeg" if self.media_type == 'audio' else "video/mp4")
            ))

        rss = PyRSS2Gen.RSS2(
            title=self.title,
            link=self.url,
            description=self.description,
            lastBuildDate=datetime.datetime.now(),
            items=items
        )

        rss.write_xml(file)
