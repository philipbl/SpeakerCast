#!/usr/bin/env python

from rsser import RSSer
from collections import namedtuple
import sys
import datetime
import argparse

Item = namedtuple('Item', ['title', 'description', 'url', 'media_url', 'date'])

parser = argparse.ArgumentParser(description='Convert a list of files into a' \
        'podcast. Files must be in the public folder of Dropbox.')

parser.add_argument('-t', '--title', required=True, help='The title of the podcast')
parser.add_argument('-f', '--files', nargs='+', required=True, help='List of files')
parser.add_argument('-d', '--description', default='', help='The description of the podcast')
parser.add_argument('-u', '--url', default='', help='The URL of the podcast')
parser.add_argument('--media-type', default='audio', help='The type of podcast media (audio or video)')

args = parser.parse_args()

items = []
for i, f in enumerate(args.files):
    items.append(Item(title='Part {} of {}'.format(i+1, len(args.files)),
                      description='',
                      url='',
                      media_url='https://dl.dropboxusercontent.com/u/2208000/{}'.format(f),
                      date=datetime.datetime.now()))

rss = RSSer(
    author=None,
    title=args.title,
    description=args.description,
    url=args.url,
    items=items,
    media_type=args.media_type
)

rss.create(sys.stdout)
