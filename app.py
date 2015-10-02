#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import Flask, request, json
from flask.ext.cors import CORS
import database
import rsser
import logging

logging.basicConfig(level=logging.INFO)
logging.getLogger("gospellibrary").setLevel(logging.WARNING)
logging.getLogger("requests").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

# Update data before application is allowed to start
logger.info("Updating database...")
database.update_database()

logger.info("Starting server...")
app = Flask(__name__)
CORS(app)


@app.route('/speakercast/speakers')
def speakers():
    logger.info("Getting speakers")
    speakers = [{'name': name, 'talks': count}
                for count, name in database.get_all_speaker_and_counts()]
    return json.dumps(speakers)


@app.route('/speakercast/generate', methods=['POST', 'OPTIONS'])
def generate():
    if request.method == 'OPTIONS':
        return ""

    data = json.loads(request.data)
    speakers = data['speakers']

    if len(speakers) == 0:
        return ""

    id_ = database.generate_id(speakers)
    logger.info("Generated id ({}) for {}".format(id_, speakers))
    return id_


@app.route('/speakercast/feed/<id>')
def feed(id):
    speakers = database.get_speakers(id)

    if speakers is None:
        # TODO: Send some error
        return "ERROR"

    talks = database.get_talks(speakers)
    logger.info("Creating RSS feed for {}".format(id))
    return rsser.create_rss_feed(talks=talks, speakers=list(speakers))


if __name__ == "__main__":
    app.run(debug=True)
