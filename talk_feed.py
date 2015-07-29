#!/usr/bin/env python3

import re
import datetime
import optparse
import concurrent.futures
from collections import namedtuple
from urllib.request import urlopen
from rsser import RSSer
import urllib.parse
from lxml import html

APRIL = 4
OCTOBER = 10


def download_page(url):
    return urlopen(url).readall().decode('utf-8')

def enum(**enums):
    return type('Enum', (), enums)

media_types = enum(AUDIO="audio", VIDEO_LOW="low", VIDEO_MEDIUM="medium", VIDEO_HIGH="high")

Talk = namedtuple('Talk', ['title', 'description', 'url', 'media_url', 'date'])


class TalkFeed():
    def __init__(self, speaker, media=media_types.AUDIO, start_year=1971,
                 end_year=datetime.date.today().year, file_name="feed.rss",
                 quiet=False):
        self.speaker = speaker
        self.media = media
        self.start_year = start_year
        self.end_year = end_year
        self.file_name = file_name
        self.quiet = quiet

        self.parser = TalkParser(self.speaker, self.media)
        self.url = "https://www.lds.org/general-conference/sessions/" + \
                   "{year}/{month:02}?lang=eng"

    def _get_talks(self):
        def download_and_parse(url, year, month):
            page = download_page(url)

            if not self.quiet:
                print(u"Downloaded {month} {year} Conference".format(month="April" if month == APRIL else "October",
                                                                     year=year))
            talks = list(self.parser.parse(page))

            if not self.quiet:
                for talk in talks:
                    print('~~~~> Found talk titled "{}"'.format(talk.title))

            return talks


        if not self.quiet:
            print("Finding talks for {speaker}\n".format(speaker=self.speaker))

        urls = []
        for year in range(self.start_year, self.end_year+1):
            for month in [APRIL, OCTOBER]:
                if year == datetime.date.today().year and month > datetime.date.today().month:
                    break

                url = self.url.format(year=year, month=month)
                urls.append((url, year, month))

        if not self.quiet:
            print("Downloading conferences...")

        talks = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
            futures = [executor.submit(download_and_parse, url, year, month) for url, year, month in urls]

            for future in concurrent.futures.as_completed(futures):
                new_talks = future.result()
                talks += new_talks

        if not self.quiet:
            print()

        talks = sorted(talks, key=lambda talk: talk.date)
        return talks

    def _get_image(self, url):
        if url is None:
            return None

        page = html.fromstring(download_page(url))

        author_url = page.xpath('//a[@rel="author"]')[0].get('href')
        author_page = html.fromstring(download_page(author_url))

        img_url = author_page.xpath('//img[contains(@class, "ga-bio__image")]')[0].get('src')
        return "http://lds.org" + img_url


    def create_feed(self):
        talks = self._get_talks()
        image = self._get_image(talks[0].url)

        rss = RSSer(
            author=self.speaker,
            title="General Conference Talks Given by {0}".format(self.speaker),
            description="Talks given by {speaker} ({media})".format(speaker=self.speaker,
                                                                    media="audio" if self.media == media_types.AUDIO else "video"),
            url="http://www.lds.org/general-conference",
            items=talks,
            media_type=self.media,
            image=image
        )

        if not self.quiet:
            print("Saving {0} feed as {1}".format("audio" if self.media == media_types.AUDIO else "video",
                                                  self.file_name))

        if self.file_name is None:
            return rss.create()
        else:
            open(self.file_name, 'w+').write(rss.create())



class TalkParser():
    def __init__(self, speaker, media):
        self.speaker = speaker
        self.media = media

    def parse(self, data):
        talks = []
        data = html.fromstring(data)

        month, year = self._get_month_year(data)

        # Get all talks
        talks = ((talk, session) for talk, session in self._get_talks(data))

        # Filter talks by speaker
        talks = ((talk, session) for talk, session in talks if self.speaker in self._get_speaker(talk))

        # Get all other information
        for talk, session in talks:
            title = self._get_title(talk)
            url = self._get_url(talk)
            description = self._get_description(url)
            date = self._get_date(session, year, month)
            media_url = self._get_media_url(talk)

            yield Talk(title=title,
                       description=description,
                       url=url,
                       media_url=media_url,
                       date=date)


    def _get_month_year(self, data):
        year_month = data.xpath('//*[@id="conference-selector"]/h1/a/text()')[0]
        month = year_month.split()[0]
        year = year_month.split()[1]

        month = 4 if month == 'April' else 10
        year = int(year)

        return month, year


    def _get_talks(self, data):
        sessions = data.xpath('//*/table[@class="sessions"][@id]')

        for session in sessions:
            talks = session.xpath('./tr/td/span[@class="talk"]/../..')

            for talk in talks:
                yield talk, session.get('id')


    def _get_speaker(self, data):
        speaker =  data.xpath('./td/span[@class="speaker"]/text()')[0]
        speaker = speaker.replace(u'\xa0', ' ') #remove nbsp
        return speaker


    def _get_title(self, talk):
        title = talk.xpath('./td/span[@class="talk"]/a/text()')[0]
        title = title.encode('ascii', 'xmlcharrefreplace').decode('utf-8')

        return title


    def _get_media_url(self, talk):
        download = talk.xpath('./td[@class="download"]')[0]
        audio_url = download.xpath('.//*[@class="audio-mp3"]')[0].get('href')

        try:
            video_1080_url = download.xpath('.//*[@class="video-1080p"]')[0].get('href')
        except IndexError:
            video_1080_url = False

        try:
            video_720_url = download.xpath('.//*[@class="video-720p"]')[0].get('href')
        except IndexError:
            video_720_url = False

        video_360_url = download.xpath('.//*[@class="video-360p"]')[0].get('href')

        if self.media == media_types.AUDIO:
            return audio_url

        elif self.media == media_types.VIDEO_LOW:
            return video_360_url or video_720_url or video_1080_url

        elif self.media == media_types.VIDEO_MEDIUM:
            return video_720_url or video_360_url or video_1080_url

        elif self.media == media_types.VIDEO_HIGH:
            return video_1080_url or video_720_url or video_360_url

        else:
            print("We have a problem! Media type is not recognized. Exiting...")
            exit()


    def _get_url(self, talk):
        try:
            url = talk.xpath('./td/span[@class="talk"]/a')[0].get('href')
            return url
        except IndexError:
            return None


    def _get_description(self, url):
        if url is None:
            return "No description"

        page = download_page(url)
        page = html.fromstring(page)

        try:
            description = page.xpath('//*[@class="kicker"]/text()')[0]
            description = description.encode('ascii', 'xmlcharrefreplace').decode('utf-8')
            return description
        except IndexError:
            return "No description"


    def _get_date(self, session, year, month):
        first_of_month = datetime.datetime(year, month, 1)
        days_ahead = 6 - first_of_month.weekday()
        sunday = first_of_month + datetime.timedelta(days_ahead)

        if session in ['womens', 'saturday-morning', 'saturday-afternoon',
                       'priesthood']:
            return sunday - datetime.timedelta(1)
        else:
            return sunday


if __name__ == '__main__':
    parser = optparse.OptionParser(usage='%prog -s "speaker name" [-o out_file] '
                                         '[--start=start_year] [--end=end_year] '
                                         '[-v low|medium|high] [-qa]', version="%prog v1.0")

    parser.add_option('-s', '--speaker', type='string',
                      help='Speaker you want to make the feed for. '
                      'Typically, the more specific you can be the better so '
                      'that no false positives arise. '
                      'For example, rather than putting "Holland", it would '
                      'be better to put "Jeffrey R. Holland".')

    parser.add_option('-o', '--out', type='string', dest='file_name', default="feed.rss",
                      help='Output file name')

    parser.add_option('--start', type='int', dest='start_year', default=1971,
                      help='Start year')

    parser.add_option('--end', type='int', dest='end_year', default=datetime.date.today().year,
                      help='End year')

    parser.add_option('-q', '--quiet', action="store_true", default=False,
                      help='Silence all print outs')

    parser.add_option('-a', '--audio', action="store_true", default=True,
                      help='Get the audio for all talks (default)')

    parser.add_option('-v', '--video', choices=['low', 'medium', 'high'],
                      help='Get the video for all talks. '
                           'There are three choices for quality of video: "low", "medium", or "high". '
                           'Low or medium is a good choice for handheld devices. '
                           'Not all video qualities are available, in which case the next best '
                           'quality will be selected. '
                           'This will override the audio flag if both are provided.')

    (options, args) = parser.parse_args()

    speaker = options.speaker
    file_name = options.file_name
    start_year = options.start_year
    end_year = options.end_year
    quiet = options.quiet
    audio = options.audio
    video = options.video

    media = media_types.AUDIO

    if not speaker:
        parser.print_help()
        exit()

    if video == 'low':
        media = media_types.VIDEO_LOW
    elif video == 'medium':
        media = media_types.VIDEO_MEDIUM
    elif video == 'high':
        media = media_types.VIDEO_HIGH

    TalkFeed(
        speaker=speaker,
        media=media,
        start_year=start_year,
        end_year=end_year,
        file_name=file_name,
        quiet=quiet
    ).create_feed()
