#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A tool for creating podcasts of speakers from General Conference.

Usage:
    speakercast.py list
    speakercast.py update [--force]
    speakercast.py generate <speaker> ...
    speakercast.py get <url>

Options:
    -h , --help     Show this message
    list            Lists all valid speakers

    update          Checks to see if there is an update to the church's database. If there is,
                    the database is updated. It takes a few minutes to update the database.
        --force     Forces an update even if there is no update to the church's database.

    generate        Creates a podcast feed based on the speakers provided. The name has
                    to be the full name (and correctly spelled) of the speaker. For
                    example, "Jeffrey R. Holland". This will provide you with a URL to
                    the feed.

    get             Downloads the feed for the specified URL.
"""


import docopt
import database
from jinja2 import Environment, FileSystemLoader, Template
from datetime import datetime
import rsser


def generate(speakers):
    all_speakers = set([s for c, s in database.get_all_speaker_and_counts()])
    speakers = set(speakers)

    # Check to make sure all given speakers are valid
    left = speakers - all_speakers
    if len(left) != 0:
        print("Unable to find {}".format(', '.join(left)))
        return

    id_ = database.generate_id(speakers)

    print("http://something/feed/{}".format(id_))


def get(url):
    id_ = url.split('/')[-1]

    speakers = database.get_speakers(id_)

    if speakers is None:
        print("Unrecognized URL: {}".format(url))
        return

    talks = database.get_talks(speakers)
    rss_feed = rsser.create_rss_feed(talks, speakers)
    print(rss_feed)


def list_speakers():
    print("{:<30}{:<10}".format("Speaker", "# of talks"))
    print("="*40)
    for count, speaker in database.get_all_speaker_and_counts():
        print("{:<30}{:<10}".format(speaker, count))


def update_database(force):
    database.update_database(force)


if __name__ == '__main__':
    args = docopt.docopt(__doc__)

    if args['generate']:
        generate(args['<speaker>'])
    elif args['get']:
        get(args['<url>'])
    elif args['list']:
        list_speakers()
    elif args['update']:
        update_database(args["--force"])
