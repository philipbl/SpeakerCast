#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from jinja2 import Environment, FileSystemLoader, Template
from email.utils import formatdate
from datetime import datetime
import time


env = Environment(loader=FileSystemLoader('templates'))
env.filters['formatdate'] = lambda dt: formatdate(time.mktime(dt.timetuple()))
feed_template = env.get_template('template.rss')


def create_rss_feed(talks, speakers):
    rss_feed = feed_template.render(talks=talks, speakers=list(speakers), now=datetime.utcnow())
    return rss_feed
