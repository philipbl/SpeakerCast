#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from jinja2 import Environment, FileSystemLoader, Template
from email.utils import formatdate
from datetime import datetime
import time

def format_title(speakers):
    if len(speakers) == 1:
        return speakers[0]
    elif len(speakers) == 2:
        return "{s[0]} and {s[1]}".format(s=speakers)
    else:
        return ", ".join(speakers[:-1]) + ", and " + speakers[-1]

env = Environment(loader=FileSystemLoader('templates'))
env.filters['format_date'] = lambda dt: formatdate(time.mktime(dt.timetuple()))
env.filters['format_title'] = format_title
feed_template = env.get_template('template.rss')


def create_rss_feed(talks, speakers):
    rss_feed = feed_template.render(talks=talks, speakers=list(speakers), now=datetime.utcnow())
    return rss_feed
