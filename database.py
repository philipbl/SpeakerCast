#!/usr/bin/env python3

from gospellibrary import Catalog
from datetime import date, datetime, timedelta
from itertools import cycle
from pymongo import MongoClient
from pprint import pprint
import requests


def _get_month_year():
    today = date.today()

    # start_year = 1971
    start_year = 2014
    end_year = today.year
    month = today.month

    # TODO: Make this simpler
    for year in range(start_year, end_year + 1):
        if year == end_year:
            if month >= 4:
                yield 4, year

            if month >= 10:
                yield 10, year
        else:
            yield 4, year
            yield 10, year


def _clean_speaker(speaker):
    speaker = speaker.replace(u'\xa0', u' ')
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
    speaker = clean_speaker(talk.secondary_title_component)
    talk_url = talk.web_url
    talk_html = package.html(uri=talk.uri)
    preview = nav_item.preview


    # Get time information
    date = (year, month)
    session = clean_session(nav_section.title)
    time = get_time(date[0], date[1], session)

    # Get audio information if available
    try:
        audio = package.related_audio_items(talk.id)[0]
        audio_url = audio.media_url
        audio_size = audio.file_size
    except:
        audio_url = None
        audio_size = None

    return {'title': title,
            'speaker': speaker,
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


def _get_speaker_image(speaker):
    speaker = speaker.lower()
    speaker = speaker.replace(' ', '-')
    speaker = speaker.replace('.', '')

    url = 'https://www.lds.org/bc/content/shared/content/images/leaders/{}-large.jpg'.format(speaker)
    # r = requests.get(url)
    # if r.status_code == 200:
    #     return url
    # else:
    #     return None
    return url


def create_database():
    print("Creating database...")
    catalog = Catalog()

    client = MongoClient()
    db = client.media
    talks_db = db.conference_talks
    speakers_db = db.conference_speakers

    # Create main database
    for month, year in get_month_year():
        item_uri = "/general-conference/{}/{:02}".format(year, month)
        print("~~~> Getting {}".format(item_uri))

        item = catalog.item(uri=item_uri, lang='eng')
        with item.package() as package:
            talks = (get_talk_info(subitem, package, year, month) for subitem in package.subitems())
            talks = (talk for talk in talks if talk['audio_url'] is not None)
            talks = (talk for talk in talks if talk['time'] is not None)
            talks = (talk for talk in talks if valid_talk(talk))
            talks = (dict(talk, image=get_speaker_image(talk['speaker'])) for talk in talks)

            talks_db.insert_many(list(talks))

    # Create database, grouped by speaker
    speakers = talks_db.aggregate([
        {
            "$group":
            {
                "_id": "$speaker",
                "talks":
                    {
                        "$push":
                            {
                                "speaker": "$speaker",
                                "title": "$title",
                                "session": "$session",
                                "time": "$time",
                                "url": "$url",
                                "html": "$html",
                                "preview": "$preview",
                                "audio_url": "$audio_url",
                                "audio_size": "$audio_size"
                            }
                    },
                "total": {"$sum": 1}
            }
        }
    ])

    speakers_db.insert(speakers)


def get_talk(speaker):
    client = MongoClient()
    db = client.media
    speakers = db.conference_speakers

    speakers = speakers.find({"_id": speaker}, {"talks": 1})
    speakers = (speaker['talks'] for speaker in speakers)
    speaker = (talk for speaker in speakers for talk in speaker)

    return list(speaker)


def get_talks(speakers):
    all_talks = [get_talk(speaker) for speaker in speakers]
    talks = [talk for talks in all_talks for talk in talks]

    return talks


def get_all_speaker_and_counts():
    client = MongoClient()
    db = client.media
    speakers = db.conference_speakers

    speakers = speakers.find({}, {"_id": 1, "total": 1})
    speakers = [(speaker['total'], speaker['_id']) for speaker in speakers]
    speakers = sorted(speakers, reverse=True)

    return speakers


def clear_database():
    client = MongoClient()
    db = client.media
    talks = db.conference_talks
    talks.remove({})

    speakers = db.conference_speakers
    speakers.remove({})


def update_database():
    # TODO: Check to see if it has been updated
    pass

# clear_database()
# create_database()

