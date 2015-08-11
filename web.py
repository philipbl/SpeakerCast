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


@app.route('/speakers')
def speakers():
    speakers = [{'name': name, 'talks': count}
                for count, name in database.get_all_speaker_and_counts()]
    return json.dumps(speakers)


@app.route('/generate/', methods=['POST'])
def generate():
    data = json.loads(request.data)
    speakers = data['speakers']

    id_ = database.generate_id(speakers)
    return id_


@app.route('/feed/<id>')
def feed(id):
    speakers = database.get_speakers(id)
    talks = database.get_talks(speakers)

    return rsser.create_rss_feed(talks=talks, speakers=list(speakers))


if __name__ == "__main__":
    app.run(debug=True)
