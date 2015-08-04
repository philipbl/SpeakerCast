#!/usr/bin/env python3

from gospellibrary import Catalog
from datetime import date
from itertools import cycle

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

def get_talk_info(talk, package, year, month):

    title = talk.primary_title_component
    speaker = talk.secondary_title_component
    conference = (year, month)
    talk_url = talk.web_url
    talk_html = package.html(uri=talk.uri)

    try:
        audio = package.related_audio_items(talk.id)[0]
    except:
        print(speaker)
        print(talk_url)

    audio_url = audio.media_url
    audio_size = audio.file_size

    return {'title': title,
            'speaker': speaker,
            'conference': conference,
            'talk_url': talk_url,
            'talk_html': talk_html,
            'audio_url': audio_url,
            'audio_size': audio_size}


def create_database():
    print("Creating database...")
    catalog = Catalog()

    for month, year in get_month_year():
        item_uri = "/general-conference/{}/{:02}".format(year, month)
        print("~~~> Getting {}".format(item_uri))

        item = catalog.item(uri=item_uri, lang='eng')
        with item.package() as package:
            conference_talks = [get_talk_info(subitem, package, year, month)
                                for subitem in package.subitems()]



        exit()




create_database()
# Speaker | Conference | Talk URL | Talk HTML |  Media URL | File Size
