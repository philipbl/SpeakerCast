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


def create_feed(speakers):
    pass


def list_speakers():
    pass


def update_database(force):
    pass


if __name__ == '__main__':
    args = docopt.docopt(__doc__)

    if args['create']:
        create_feed(args['<speaker>'])
    elif args['list']:
        list_speakers()
    elif args['update']:
        update_database(args["--force"])
