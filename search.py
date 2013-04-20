#!/usr/bin/python

import re
import datetime
import optparse

APRIL = 4
OCTOBER = 10


class Talk():
    def __init__(self, title, description, url, audio_url, date):
        self.title = title
        self.description = description
        self.url = url
        self.audio_url = audio_url
        self.date = date

    def get_title(self):
        return self.title

    def set_title(self, title):
        self.title = title

    def get_description(self):
        return self.description

    def set_description(self, description):
        self.description = description

    def get_url(self):
        return self.url

    def set_url(self, url):
        self.url = url

    def get_audio_url(self):
        return self.audio_url

    def set_audio_url(self, audio_url):
        self.audio_url = audio_url

    def get_date(self):
        return self.date

    def set_date(self, date):
        self.date = date


class TalkFeed():
    def __init__(self, speaker, start_year=1971, end_year=datetime.date.today().year, file_name="feed.rss", quiet=False):
        self.speaker = speaker
        self.start_year = start_year
        self.end_year = end_year
        self.file_name = file_name
        self.quiet = quiet

        self.url = "https://www.lds.org/general-conference/sessions/" + \
                   "{year}/{month:02}?lang=eng"

    def __get_talks(self):
        talks = []
        for year in range(self.start_year, self.end_year+1):
            for month in [APRIL, OCTOBER]:
                if year == datetime.date.today().year and month > datetime.date.today().month:
                    break

                url = self.url.format(year=year, month=month)

                if not self.quiet:
                    print u"Downloading {month} {year} Conference".format(month="April" if month == APRIL else "October",
                                                                          year=year)

                page = Downloader().download_page(url)
                parser = TalkParser(page, self.speaker)

                talks += self.__create_talks(parser, year, month)

                if not self.quiet:
                    print

        return talks

    def __create_talks(self, parser, year, month):
        talks = parser.get_talks()

        for talk in talks:
            if not self.quiet:
                print u"\tFound talk by {speaker} titled: {title}".format(speaker=self.speaker,
                                                                          title=talk.get_title())
            talk.set_date(datetime.datetime(year, month, 1, 15))

        return talks

    def create_feed(self):
        talks = self.__get_talks()

        rss = RSSer(
            speaker=self.speaker,
            title="General Conference Talks Given by {0}".format(self.speaker),
            description="Talks given by {0}".format(self.speaker),
            url="http://www.lds.org/general-conference",
            talks=talks
        )

        if not self.quiet:
            print "Saving {0}".format(self.file_name)

        rss.create(open(self.file_name, 'w+'))


class Downloader():
    def download_page(self, url):
        from urllib import urlopen

        return urlopen(url).read().decode('utf-8')


class TalkParser():
    def __init__(self, data, speaker):
        self.data = data
        self.speaker = speaker

        self.speaker_data = self.__get_speaker_data()

    def get_talks(self):
        talks = []
        for talk in self.speaker_data:
            talks.append(
                Talk(
                    title=self.__get_title(talk),
                    description=self.__get_description(talk),
                    url=self.__get_url(talk),
                    audio_url=self.__get_audio_url(talk),
                    date=self.__get_date(talk)
                )
            )

        return talks

    def __get_speaker_data(self):
        speakers = re.findall("<tr>.*?</tr>", self.data, re.S)

        speaker_data = []
        for s in speakers:
            if s.find(self.speaker) != -1:
                speaker_data.append(s)

        return speaker_data

    def __get_title(self, talk):
        title_html = re.search("<span class=\"talk\"><a href=\".*?\">.*?</a></span>",
                               talk,
                               re.S).group()

        m = re.search("(<span class=\"talk\">)" +
                      "(<a href=\".*?\">)" +
                      "(.*?)" +
                      "(</a></span>)", title_html, re.S)

        return m.group(3)

    def __get_audio_url(self, talk):
        m = re.search("\"(https?://\\S*?\\.mp3\\S*?)\"", talk, re.S)

        return m.group(1)

    def __get_url(self, talk):
        title_html = re.search("<span class=\"talk\"><a href=\".*?\">.*?</a></span>",
                               talk,
                               re.S).group()

        m = re.search("(<span class=\"talk\">)" +
                      "<a href=\"(.*?)\">" +
                      "(.*?)" +
                      "(</a></span>)", title_html, re.S)

        return m.group(2)

    def __get_description(self, talk):
        link = self.__get_url(talk)
        page = Downloader().download_page(link)
        m = re.search("<div class=\"kicker\" id=\"\">(.*?)</div>", page, re.S)

        if m is None:
            m = re.search("/(\\d{4})/(\\d{2})/", link, re.S)
            year = m.group(1)
            month = m.group(2)

            return "Talk given {month} {year} Conference".format(month="April" if month == "04" else "October",
                                                                 year=year)

        return m.group(1)

    def __get_date(self, talk):
        pass


class RSSer():
    def __init__(self, speaker, title, description, url, talks):
        self.speaker = speaker
        self.title = title
        self.description = description
        self.url = url
        self.talks = talks

    def create(self, file):
        import PyRSS2Gen

        items = []

        for talk in self.talks:
            items.append(PyRSS2Gen.RSSItem(
                title=talk.get_title(),
                link=talk.get_url(),
                description=talk.get_description(),
                guid=PyRSS2Gen.Guid(talk.get_url(), False),
                pubDate=talk.get_date(),
                enclosure=PyRSS2Gen.Enclosure(talk.get_audio_url(), 0, "audio/mpeg")
            ))

        rss = PyRSS2Gen.RSS2(
            title=self.title,
            link=self.url,
            description=self.description,
            lastBuildDate=datetime.datetime.now(),
            items=items
        )

        rss.write_xml(file)

if __name__ == '__main__':
    parser = optparse.OptionParser(usage="%prog -s \"<speaker name>\" -o feed.rss [options]", version="%prog 1.0")

    parser.add_option('-s', '--speaker', type='string', dest='speaker',
                      help='Speaker you want to make the feed for')

    parser.add_option('-o', '--out', type='string', dest='file_name', default="feed.rss",
                      help='Output file name')

    parser.add_option('--start', type='int', dest='start_year', default=1971,
                      help='Start year')

    parser.add_option('--end', type='int', dest='end_year', default=datetime.date.today().year,
                      help='End year')

    parser.add_option('-q', '--quiet', action="store_true", dest='quiet', default=False,
                      help='Silence all print outs')

    (options, args) = parser.parse_args()

    speaker = options.speaker
    file_name = options.file_name
    start_year = options.start_year
    end_year = options.end_year
    quiet = options.quiet

    if not speaker:
        parser.print_help()
        exit()

    TalkFeed(
        speaker=speaker,
        start_year=start_year,
        end_year=end_year,
        file_name=file_name,
        quiet=quiet
    ).create_feed()
