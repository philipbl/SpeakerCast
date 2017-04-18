#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from jinja2 import Environment, FileSystemLoader, Template
from flask.ext.moment import Moment
from email.utils import formatdate
from datetime import datetime
import time

env = Environment(loader=FileSystemLoader('templates'))
env.filters['format_date'] = lambda dt: formatdate(time.mktime(dt.timetuple()))[:-5] + "MST"
feed_template = env.get_template('template.rss')


def create_rss_feed(talks, speaker):
    rss_feed = feed_template.render(talks=talks,
                                    speaker=speakers,
                                    now=datetime.utcnow())
    return rss_feed
