#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import Flask, request, json, url_for
from flask.ext.cors import CORS
import database
import rsser
import logging
import logging.config
import yaml
import threading

# Log configuration
logging.config.dictConfig(yaml.load(open('logging.yaml')))
logger = logging.getLogger("speakercast." + __name__)

check_time = 60 * 60

# Update data base in background
logger.info("Updating database in background...")
logger.info("Checking for updates every {} seconds".format(check_time))
threading.Thread(target=lambda: database.update_database(check_time=check_time)).start()

logger.info("Starting server...")
app = Flask(__name__)
CORS(app)


@app.route('/speakers')
def speakers():
    logger.info("Getting speakers")
    speakers = [{'name': name, 'talks': count}
                for count, name in database.get_all_speaker_and_counts()]
    return json.dumps(speakers)


@app.route('/generate', methods=['POST', 'OPTIONS'])
def generate_id():
    if request.method == 'OPTIONS':
        return ""

    data = json.loads(request.data)
    speaker = data.get('speaker')

    if speaker is None:
        logger.error("No \"speaker\" field in request data!")
        return json.dumps({"error": "No \"speaker\" field in request data!"})

    if speaker == "":
        logger.warning("Speaker name was empty. Ignoring request.")
        return json.dumps({"error": "Speaker name was empty. Ignoring request."})

    id_ = database.generate_id(speaker)
    logger.info("Generated id ({}) for {}".format(id_, speaker))
    return id_


@app.route('/feeds/<id>')
def generate_feed(id):
    speaker = database.get_speaker(id)

    if speaker is None:
        # TODO: Send some error
        logger.error("No speaker match {}!".format(id))
        return json.dumps({"error": "No speaker match {}!".format(id)})

    talks = database.get_talks(speaker)
    logger.info("Creating RSS feed for {}: {}".format(id, speaker))
    return rsser.create_rss_feed(talks=talks, speaker=speaker)


if __name__ == "__main__":
    app.run(debug=True)
