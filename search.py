#!/usr/bin/python


from urllib import urlopen
import re
import datetime
import PyRSS2Gen

URL_BASE = "https://www.lds.org/general-conference/sessions/"
SPEAKER_RE = "<tr>.*?</tr>"
TITLE_RE = "<span class=\"talk\"><a href=\".*?\">.*?</a></span>"

SPEAKER = "Holland"


def get_title(html):
    title_html = re.search(TITLE_RE, html, re.S).group()
    m = re.search("(<span class=\"talk\">)" +
                  "(<a href=\".*?\">)" +
                  "(.*?)" +
                  "(</a></span>)", title_html, re.S)
    return m.group(3)


def get_audio_url(html):
    m = re.search("\"(https?://\\S*?\\.mp3\\S*?)\"", html, re.S)
    return m.group(1)


def create_rss(info):
    items = []
    for title, url, month, year in info:
        if year == datetime.date.today().year and month > datetime.date.today().month:
            continue

        items.append(PyRSS2Gen.RSSItem(
            title=title,
            link=url,
            description="Talk given in {year} conference".format(year=year),
            guid=PyRSS2Gen.Guid(url, False),
            pubDate=datetime.datetime(year, month, 1),
            enclosure=PyRSS2Gen.Enclosure(url, 0, "audio/mpeg")
        ))

    rss = PyRSS2Gen.RSS2(
        title="Conference Talks Given by {speaker}".format(speaker=SPEAKER),
        link="http://generalconference.lds.org",
        description="All the conference talks for {speaker} on lds.org.".format(speaker=SPEAKER),
        lastBuildDate=datetime.datetime.now(),
        items=items
    )

    rss.write_xml(open("feed.rss", "w+"))


speaker_info = []
for year in range(1975, 2014):
    for month in [4, 10]:
        url = URL_BASE + "{year}/{month:02}?lang=eng".format(year=year,
                                                             month=month)
        page = urlopen(url).read().decode('utf-8')

        print 'Downloaded page ({0})'.format(url)
        speakers = re.findall(SPEAKER_RE, page, re.S)

        for speaker in speakers:
            if speaker.find(SPEAKER) != -1:
                title = get_title(speaker)
                url = get_audio_url(speaker)

                print "\tAdding", title
                speaker_info.append((title, url, month, year))

        print

create_rss(speaker_info)
