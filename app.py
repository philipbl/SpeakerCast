#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import Flask, request, json
from flask.ext.cors import CORS
import database
import rsser

# Update data before application is allowed to start
database.update_database()

app = Flask(__name__)
CORS(app)


@app.route('/speakercast/speakers')
def speakers():
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
    print("Generated id ({}) for {}".format(id_, speakers))
    return id_


@app.route('/speakercast/feed/<id>')
def feed(id):
    speakers = database.get_speakers(id)

    if speakers is None:
        # TODO: Send some error
        return "ERROR"

    talks = database.get_talks(speakers)
    return rsser.create_rss_feed(talks=talks, speakers=list(speakers))


if __name__ == "__main__":
    app.run(debug=True)
