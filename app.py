#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import Flask, request, json
from flask.ext.cors import CORS
import database
import rsser
import logging
import threading

logging.basicConfig(level=logging.INFO)
logging.getLogger("gospellibrary").setLevel(logging.WARNING)
logging.getLogger("requests").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

# Update data base in background
logger.info("Updating database in background...")
threading.Thread(target=database.update_database).start()

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
    speakers = data.get('speakers')

    if speakers is None:
        logger.error("No \"speakers\" field in request data!")
        return json.dumps({"error": "No \"speakers\" field in request data!"})

    if len(speakers) == 0:
        logger.warning("Speaker list was empty. Ignoring request.")
        return json.dumps({"error": "Speaker list was empty. Ignoring request."})

    id_ = database.generate_id(speakers)
    logger.info("Generated id ({}) for {}".format(id_, speakers))
    return id_


@app.route('/speakercast/feed/<id>')
def feed(id):
    speakers = database.get_speakers(id)

    if speakers is None:
        # TODO: Send some error
        logger.error("No speakers match {}!".format(id))
        return json.dumps({"error": "No speakers match {}!".format(id)})

    talks = database.get_talks(speakers)
    logger.info("Creating RSS feed for {}: {}".format(id, speakers))
    return rsser.create_rss_feed(talks=talks, speakers=list(speakers))


if __name__ == "__main__":
    app.run(debug=True)
