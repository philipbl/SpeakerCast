# Purpose

`talk_feed` is a small python script that searches through the archives of the [LDS Church's General Conferences][1] looking for talks by the specified speaker and creates an audio or video feed. This is meant as an easy way to obtain all the talks for a specific speaker over the years.


# Usage

To run `talk_feed`, the only necessary argument is the speaker

```
talk_feed -s "Jeffrey R. Holland"
```

There are many more arguments that can be used to customize the feed, such as:
- start year
- end year
- create audio feed (default)
- create low (360p), medium (720p), or high (1080p) quality video feed

To view all the options, run

```
talk_feed --help
```

Note: Python is necessary to run this script.


# Content

All content (text, audio, video, etc.) is provided by and copyrighted by [The Church of Jesus Christ of Latter-day Saints][2].

[1]: https://www.lds.org/general-conference/
[2]: https://www.lds.org/
