#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from gospellibrary import Catalog
from datetime import date, datetime, timedelta
from itertools import cycle
from tinydb import TinyDB, where
from tinydb_serialization import Serializer, SerializationMiddleware
import requests
import random
import os
import logging
import threading
from collections import defaultdict

TINYDB_PATH = './db.json'

logger = logging.getLogger("speakercast." + __name__)

class DateTimeSerializer(Serializer):
    OBJ_CLASS = datetime

    def encode(self, obj):
        return obj.strftime('%Y-%m-%dT%H:%M:%S')

    def decode(self, s):
        return datetime.strptime(s, '%Y-%m-%dT%H:%M:%S')


serialization = SerializationMiddleware()
serialization.register_serializer(DateTimeSerializer(), 'TinyDate')



def _get_month_year(start, end):
    start_year, start_month = start
    end_year, end_month = end

    # Make sure we start on a boundary
    if start_month <= 4:
        start_month = 4
    elif start_month <= 10:
        start_month = 10
    else:
        start_month = 4
        start_year += 1

    # Make sure we end on a boundary
    if end_month < 4:
        end_month = 10
        end_year -= 1
    elif end_month < 10:
        end_month = 4
    else:
        end_month = 10

    yield (start_month, start_year)

    while start_year != end_year or start_month != end_month:
        start_month += 6
        start_year = start_year + start_month // 12
        start_month = start_month % 12

        yield (start_month, start_year)


def _clean_speaker(speaker):
    speaker = speaker.replace('\xa0', ' ')
    speaker = speaker.replace('By ', '')
    speaker = speaker.replace('President ', '')
    speaker = speaker.replace('Elder ', '')
    speaker = speaker.replace('Presented by ', '')
    speaker = speaker.strip()

    return speaker


def _clean_session(session):
    session = session.lower()
    if session in ['priesthood', 'general priesthood session',
                   'general priesthood meeting']:
        session = 'priesthood session'

    elif session == 'welfare session':
        session = 'general welfare session'

    elif session == 'saturday morning':
        session = 'saturday morning session'

    elif session in ['general women\'s meeting', 'women\'s fireside address',
                   'general relief society meeting', 'general women\'s session',
                   'general women’s meeting', 'general women’s meeting ',
                   'relief society sesquicentennial satellite broadcast']:
        session = "general young women meeting"

    session = session.replace('sesssion', 'session')
    session = session.replace('preisthood', 'priesthood')

    return session


def _get_time(year, month, session):
    first_of_month = datetime(year, month, 1)
    days_ahead = 6 - first_of_month.weekday()
    sunday = first_of_month + timedelta(days_ahead)

    def adjust_time(delta_day, hour):
        return (sunday - timedelta(delta_day)).replace(hour=hour)

    try:
        time = {"general young women meeting": adjust_time(8, 18),
                "thursday morning session": adjust_time(3, 10),
                "thursday afternoon session": adjust_time(3, 14),
                "friday morning session": adjust_time(2, 10),
                "friday afternoon session": adjust_time(2, 14),
                "saturday morning session": adjust_time(1, 10),
                "saturday afternoon session": adjust_time(1, 14),
                "priesthood session": adjust_time(1, 18),
                "sunday morning session": adjust_time(0, 10),
                "sunday afternoon session": adjust_time(0, 14),
                "general welfare session": adjust_time(0, 18),
                "tuesday morning session": adjust_time(-2, 10),
                "tuesday afternoon session": adjust_time(-2, 14)}[session.lower()]

        return time
    except:
        return None


def _get_talk_info(talk, package, year, month):
    nav_item = package.nav_items(talk.id)[0]
    nav_section = package.nav_section(nav_item.nav_section_id)[0]

    # Get talk information
    title = talk.primary_title_component
    speaker = _clean_speaker(talk.secondary_title_component)
    talk_url = talk.web_url
    talk_html = package.html(uri=talk.uri)
    preview = nav_item.preview


    # Get time information
    date = (year, month)
    session = _clean_session(nav_section.title)
    time = _get_time(date[0], date[1], session)

    # Get audio information if available
    try:
        audio = package.related_audio_items(talk.id)[0]
        audio_url = audio.media_url
        audio_size = audio.file_size
    except:
        audio_url = None
        audio_size = None

    return {'title': title,
            'speaker': speaker.replace('\xc2', ''),
            'session': session,
            'time': time,
            'url': talk_url,
            'html': talk_html,
            'preview': preview,
            'audio_url': audio_url,
            'audio_size': audio_size}


def _valid_talk(talk):
    title = talk['title']

    if title in ['Welcome to Conference', 'The Sustaining of Church Officers']:
        return False

    if 'Church Auditing Department Report' in title or \
       'Statistical Report' in title:
        return False

    return True


def _get_database():
    return TinyDB(TINYDB_PATH, storage=serialization)


def _get_speaker_db():
    return _get_database().table('conference_speakers')


def _get_metadata_db():
    return _get_database().table('metadata')


def _get_id_db():
    return _get_database().table('ids')


def _new_database_version():
    metadata = _get_metadata_db()

    new_version = Catalog().current_version()
    logger.info("New version: {}".format(new_version))

    old_version = metadata.search(where('version').exists())
    if len(old_version) == 0:
        # This will happen the first time the value is put into
        # into the database
        logger.info("No current version. Updating database...")
        metadata.insert({'version': new_version})
        return True

    old_version = old_version[0]['version']
    logger.info("Current version: {}".format(old_version))

    if new_version != old_version:
        logger.info("Database is out of date. Updating database...")

        metadata.update({'version': new_version}, where('version').exists())
        return True
    else:
        return False


def create_database(start=(1971, 4), end=(date.today().year, date.today().month)):
    logger.info("Creating database...")
    catalog = Catalog()

    speakers_db = _get_speaker_db()

    # TODO: Clean up this logic
    speakers = defaultdict(dict)
    for month, year in _get_month_year(start, end):
        item_uri = "/general-conference/{0}/{1:02}".format(year, month)
        logger.info("~~~> Getting {0}".format(item_uri))

        item = catalog.item(uri=item_uri, lang='eng')
        with item.package() as package:
            talks = (_get_talk_info(subitem, package, year, month) for subitem in package.subitems())
            talks = (talk for talk in talks if talk['audio_url'] is not None)
            talks = (talk for talk in talks if talk['time'] is not None)
            talks = (talk for talk in talks if _valid_talk(talk))

            for t in talks:
                speaker = speakers[t['speaker']]

                if 'talks' not in speaker:
                    speaker['talks'] = []

                speaker['talks'].append(t)

    speakers_db.insert_multiple([{"speaker": s, "talks": speakers[s]['talks']} for s in speakers])


def get_talk(speaker):
    speakers = _get_speaker_db()

    speaker = speakers.search(where('speaker') == speaker)
    assert len(speaker) == 1

    talks = speaker[0]['talks']
    return talks


def get_talks(speakers):
    all_talks = [get_talk(speaker) for speaker in speakers]
    talks = [talk for talks in all_talks for talk in talks]

    return talks


def get_all_speaker_and_counts():
    speakers = _get_speaker_db()
    speakers = [(len(speaker['talks']), speaker['speaker']) for speaker in speakers.all()]
    speakers = sorted(speakers, reverse=True)

    return speakers


def generate_id(speakers, id_generator=None):
    if id_generator is None:
        logger.debug("Using default ID generator")
        id_generator = lambda: random.randint(0, 16777215)

    ids = _get_id_db()

    speakers = sorted(speakers)
    id_ = ids.search(where('speakers') == speakers)

    if len(id_) != 0:
        logger.debug("There is already an ID for these speakers: {}".format(id_))
        return id_[0]["id"]
    else:
        logger.debug("Creating a new ID for speakers")
        id_ = format(id_generator(), 'x')

        # Make sure I'm not duplicating a key
        while len(ids.search(where('id') == id_)) > 0:
            logger.debug("ID {} is already in use, creating another one".format(id_))
            id_ = format(id_generator(), 'x')

        logger.debug("Done -- returning new ID {}".format(id_))
        ids.insert({'id': id_, "speakers": speakers})
        return id_


def get_ids():
    ids = _get_id_db()
    return [x['id'] for x in ids.all()]


def get_speakers(id_):
    ids = _get_id_db()
    result = ids.search(where('id') == id_)

    if len(result) > 0:
        assert len(result) == 1
        return result[0]['speakers']
    else:
        return None


def clear_database():
    logger.info("Clearing database")
    db = TinyDB(TINYDB_PATH, storage=serialization)
    db.purge_tables()


def clear_id_database():
    logger.warning("Clearing ID database")
    ids = _get_id_db()
    lds.purge()


def update_database(start=(1971, 4), end=(date.today().year, date.today().month),
                    force=False, check_time=None):
    if _new_database_version() or force:
        logger.info("Updating database to new version")
        clear_database()
        create_database(start, end)
        _new_database_version()
    else:
        logger.info("Database is already up to date")

    if check_time is not None:
        threading.Timer(check_time, lambda: update_database(check_time=check_time)).start()


