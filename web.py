#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import urllib.parse
import datetime
from flask import Flask, request
from talk_feed import TalkFeed

app = Flask(__name__)

@app.route('/')
def hello():
    return 'Hello World!'


@app.route('/rss/<speaker>')
def get_rss(speaker):
    speaker = urllib.parse.unquote_plus(speaker)
    start_year = int(request.args.get('start_year', 1971))
    end_year = int(request.args.get('end_year', datetime.date.today().year))

    return TalkFeed(speaker,
                    start_year=start_year,
                    end_year=end_year,
                    file_name=None).create_feed()


if __name__ == "__main__":
    app.run(debug=True)
