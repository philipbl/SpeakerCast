#!/usr/bin/env python3

import re
import datetime
import optparse
import concurrent.futures
from collections import namedtuple
from urllib.request import urlopen
from rsser import RSSer
import urllib.parse

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
            new_talks = [(year, month, talk) for talk in self.parser.parse(page)]

            if not self.quiet:
                for _, _, t in new_talks:
                    print('~~~~> Found talk titled "{}"'.format(t.title))

            return new_talks


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
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(download_and_parse, url, year, month) for url, year, month in urls]

            for future in concurrent.futures.as_completed(futures):
                try:
                    new_talks = future.result()
                    talks += new_talks
                except Exception as exc:
                    print('Exception while downloading {}'.format(url))
                    print(exc)

        if not self.quiet:
            print()

        talks = [talk for year, month, talk in sorted(talks, reverse=True)]
        return talks


    def create_feed(self):
        talks = self._get_talks()

        rss = RSSer(
            author=self.speaker,
            title="General Conference Talks Given by {0}".format(self.speaker),
            description="Talks given by {speaker} ({media})".format(speaker=self.speaker,
                                                                    media="audio" if self.media == media_types.AUDIO else "video"),
            url="http://www.lds.org/general-conference",
            items=talks,
            media_type=self.media
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

        for talk in self._get_speaker_data(data):

            title = self._get_title(talk)
            description = self._get_description(talk)
            url = self._get_url(talk)
            media_url = self._get_media_url(talk)
            date = self._get_date(talk)

            if media_url is None:
                continue

            talks.append(
                Talk(
                    title=title,
                    description=description,
                    url=url,
                    media_url=media_url,
                    date=date
                )
            )

        return talks

    def _get_speaker_data(self, data):
        speakers = re.findall("<tr>.*?</tr>", data, re.S)

        speaker_data = []
        for s in speakers:
            # removing nbsp
            s = s.replace(u'\xa0', ' ')

            if s.find(self.speaker) != -1:
                speaker_data.append(s)

        return speaker_data

    def _get_title(self, talk):
        title_html = re.search("<span class=\"talk\"><a href=\".*?\">.*?</a></span>",
                               talk,
                               re.S)

        if title_html is None:
            return "No title"

        title_html = title_html.group()

        m = re.search("(<span class=\"talk\">)" +
                      "(<a href=\".*?\">)" +
                      "(.*?)" +
                      "(</a></span>)", title_html, re.S)

        title = m.group(3)
        title = title.encode('ascii', 'xmlcharrefreplace').decode('utf-8')

        return title

    def _get_media_url(self, talk):
        audio_url = re.search("\"(https?://\\S*?\\.mp3\\S*?)\"", talk, re.S)
        video_1080_url = re.search("\"(https?://\\S*?-1080p-\\S*?\\.mp4\\S*?)\"", talk, re.S)
        video_720_url = re.search("\"(https?://\\S*?-720p-\\S*?\\.mp4\\S*?)\"", talk, re.S)
        video_480_url = re.search("\"(https?://\\S*?-480p-\\S*?\\.mp4\\S*?)\"", talk, re.S)
        video_360_url = re.search("\"(https?://\\S*?-360p-\\S*?\\.mp4\\S*?)\"", talk, re.S)

        audio_url = audio_url.group(1) if audio_url is not None else None
        video_1080_url = video_1080_url.group(1) if video_1080_url is not None else None
        video_720_url = video_720_url.group(1) if video_720_url is not None else None
        video_480_url = video_480_url.group(1) if video_480_url is not None else None
        video_360_url = video_360_url.group(1) if video_360_url is not None else None

        if self.media == media_types.AUDIO:
            return audio_url

        elif self.media == media_types.VIDEO_LOW:
            return video_360_url or video_480_url or video_720_url or video_1080_url

        elif self.media == media_types.VIDEO_MEDIUM:
            return video_720_url or video_480_url or video_360_url or video_1080_url

        elif self.media == media_types.VIDEO_HIGH:
            return video_1080_url or video_720_url or video_480_url or video_360_url

        else:
            print("We have a problem! Media type is not recognized. Exiting...")
            exit()

    def _get_url(self, talk):
        title_html = re.search("<span class=\"talk\"><a href=\".*?\">.*?</a></span>",
                               talk,
                               re.S)

        if title_html is None:
            return None

        title_html = title_html.group()

        m = re.search("(<span class=\"talk\">)" +
                      "<a href=\"(.*?)\">" +
                      "(.*?)" +
                      "(</a></span>)", title_html, re.S)

        return m.group(2)

    def _get_description(self, talk):
        link = self._get_url(talk)

        if link is None:
            return "No description"

        page = download_page(link)
        m = re.search('<div class="kicker">(.*?)</div>', page, re.S)

        if m is None:
            m = re.search("/(\\d{4})/(\\d{2})/", link, re.S)
            year = m.group(1)
            month = m.group(2)

            return "Talk given {month} {year} Conference".format(month="April" if month == "04" else "October",
                                                                 year=year)

        description = m.group(1)
        description = description.encode('ascii', 'xmlcharrefreplace').decode('utf-8')
        return description

    def _get_date(self, talk):
        pass


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
