#!/usr/bin/env python3
"""
A tool for creating podcasts of speakers from General Conference.

Usage:
    talk_feed.py list
    talk_feed.py update [--force]
    talk_feed.py create <speaker> ...

Options:
    -h , --help     Show this message
    list            Lists all valid speakers
    update          Checks to see if there is an update to the church's database. If there is,
                    the database is updated. It takes a few minutes to update the database.
        --force     Forces an update even if there is no update to the church's database.
    create          Creates a podcast feed based on the speakers provided. The name has
                    to be the full name (and correctly spelled) of the speaker. For
                    example, "Jeffrey R. Holland".
"""


import docopt
import database
from jinja2 import Environment, FileSystemLoader, Template
from datetime import datetime
import rsser


def create_feed(speakers):
    all_speakers = set([s for c, s in database.get_all_speaker_and_counts()])
    speakers = set(speakers)

    # Check to make sure all given speakers are valid
    left = speakers - all_speakers
    if len(left) != 0:
        print("Unable to find {}".format(', '.join(left)))
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
    if force:
        database.clear_database()
        database.create_database()
    else:
        database.update_database()


if __name__ == '__main__':
    args = docopt.docopt(__doc__)

    if args['create']:
        create_feed(args['<speaker>'])
    elif args['list']:
        list_speakers()
    elif args['update']:
        update_database(args["--force"])
