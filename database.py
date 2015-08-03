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


def create_database():
    print("Creating database...")
    catalog = Catalog()

    for month, year in get_month_year():
        item_uri = "/general-conference/{}/{:02}".format(year, month)
        print("~~~> Getting {}".format(item_uri))

        item = catalog.item(uri=item_uri, lang='eng')
        with item.package() as package:
            for subitem in package.subitems():
                audio = package.related_audio_items(subitem.id)[0]

                title = subitem.primary_title_component
                speaker = subitem.secondary_title_component
                conference = (year, month)
                talk_url = subitem.web_url
                talk_html = package.html(uri=subitem.uri)
                audio_url = audio.media_url
                audio_size = audio.file_size

                print(subitem)
                # print(package.html(uri=subitem.uri))
                # print(package.related_audio_items(subitem.id))
                # print(package.related_content_items(subitem.id))

                # TODO: Add to database
        exit()




create_database()
# Speaker | Conference | Talk URL | Talk HTML |  Media URL | File Size
