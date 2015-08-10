#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import urllib.parse
from datetime import datetime
from flask import Flask, request, json
from jinja2 import Environment, FileSystemLoader, Template
import database
import rsser

app = Flask(__name__)

# Access database to get list of speakers

@app.route('/')
def index():
    return open('templates/index.html').read()
    # index_template = env.get_template('index.html') # TODO: Move this
    # return index_template.render(speakers=[("Elder Holland", 12), ("President Eyring", 15)])


@app.route('/speakers')
def speakers():
    speakers = [{'name': name, 'talks': count}
                for count, name in database.get_all_speaker_and_counts()]
    return json.dumps(speakers)


@app.route('/feed/<speakers>')
def generate(speakers):
    speakers = speakers[:-1].split(',')
    talks = database.get_talks(speakers)

    return rsser.create_rss_feed(talks=talks, speakers=list(speakers))


if __name__ == "__main__":
    app.run(debug=True)
