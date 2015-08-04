#!/usr/bin/env python3

from gospellibrary import Catalog
from datetime import date, datetime, timedelta
from itertools import cycle
from pymongo import MongoClient


def get_month_year():
    today = date.today()

    start_year = 1971
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
            yield 4,year
            yield 10, year


def clean_up_speaker(speaker):
    speaker = speaker.replace(u'\xa0', u' ')
    speaker = speaker.replace('By ', '')
    speaker = speaker.replace('President ', '')
    speaker = speaker.replace('Elder ', '')

    return speaker


def clean_up_session(session):
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


def get_time(year, month, session):
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



def get_talk_info(talk, package, year, month):

    # Get talk information
    title = talk.primary_title_component
    speaker = clean_up_speaker(talk.secondary_title_component)
    talk_url = talk.web_url
    talk_html = package.html(uri=talk.uri)

    # Get time information
    date = (year, month)
    session = package.nav_section(package.nav_items(talk.id)[0].nav_section_id)[0].title
    session = clean_up_session(session)
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
            'talk_url': talk_url,
            'talk_html': talk_html,
            'audio_url': audio_url,
            'audio_size': audio_size}


def create_database():
    print("Creating database...")
    catalog = Catalog()

    client = MongoClient()
    db = client.media
    collection = db.conference_talks

    for month, year in get_month_year():
        item_uri = "/general-conference/{}/{:02}".format(year, month)
        print("~~~> Getting {}".format(item_uri))

        item = catalog.item(uri=item_uri, lang='eng')
        with item.package() as package:
            conference_talks = (get_talk_info(subitem, package, year, month)
                                for subitem in package.subitems())
            conference_talks = (talk for talk in conference_talks
                                if talk['audio_url'] is not None)
            conference_talks = (talk for talk in conference_talks
                                if talk['time'] is not None)

            collection.insert_many(list(conference_talks))


def get_speaker(speaker, start, end=date.today().year):
    client = MongoClient()
    db = client.media
    talks = db.conference_talks

    for talk in talks.find({"speaker": {"$regex": speaker}}):
        print(talk['speaker'])
        print(talk['session'])


def get_all_speakers():
    client = MongoClient()
    db = client.media
    talks = db.conference_talks

    speakers = talks.aggregate([
        {
            "$group":
            {
                "_id": "$speaker",
                "total": {"$sum": 1}
            }
        }
    ])

    speakers = ((speaker['total'], speaker['_id']) for speaker in speakers)
    speakers = sorted(list(speakers))

    return speakers


def update_database():
    # Check to see if it has been updated
    pass

# create_database()
get_speaker("Jeffrey R. Holland", 2012)
# get_all_speakers()

# Test different commands:
#   - Get all speakers
#   - Get all talks for specific speaker


