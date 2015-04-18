# talk_feed

## Purpose

`talk_feed` is a Python script that searches through the archives of the [LDS Church's General Conferences][1] looking for talks by the specified speaker and creates an audio or video feed. This is meant as an easy way to obtain all the talks for a specific speaker over the years.


## Usage

To run `talk_feed`, the only necessary argument is the speaker

```
talk_feed -s "Jeffrey R. Holland"
```

This will create a file (by default, `feed.rss`) that is a RSS feed to the audio files all the talks given by Jeffery R. Holland. This feed can be used like a podcast and added to any podcast managing app.

There are many more arguments that can be used to customize the output of the feed, such as:
- start year
- end year
- create audio feed (default)
- create low (360p), medium (720p), or high (1080p) quality video feed

To view all the options, run

```
talk_feed --help
```

## Web Service

`talk_feed` can easily be deployed as a web service using [Flask](http://flask.pocoo.org). To do this run:

```
python main.py
```

This creates a local webserver that will service requests at `http://localhost/rss/<speaker>?start_year=<X>&end_year=<Y>`. I have deployed `talk_feed` to Heroku and can be accessed at [`https://talk-feed.herokuapp.com`][3]. The RSS feed is generated dynamically based on the URL parameters given.


## Content

All content (text, audio, video, etc.) is provided by and copyrighted by [The Church of Jesus Christ of Latter-day Saints][2].

## To Do
- Add caching of feeds. 
- Add web interface.


[1]: https://www.lds.org/general-conference/
[2]: https://www.lds.org/
[3]: https://talk-feed.herokuapp.com
