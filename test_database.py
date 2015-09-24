#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import talk_feed as tf
import database as db
import pytest
from datetime import datetime
import os
import sys


def test_get_talk():
    # Populate database
    db.clear_database()
    db.update_database(start=(2000,4), end=(2005,4))

    # Pick a few speakers to make sure their counts are correct
    expected = {"Gordon B. Hinckley": 48,
                "Thomas S. Monson": 26,
                "Boyd K. Packer": 11,
                "L. Tom Perry": 11,
                "Joseph B. Wirthlin": 11}

    for name, count in expected.items():
        talks = db.get_talk(name)
        assert len(talks) == count

    talk = db.get_talk("Gordon B. Hinckley")[0]

    # Make sure the fields that I am expecting are here
    if sys.version_info[0] < 3:
        expected = {'session': unicode, 'preview': unicode, 'audio_url': unicode,
                    'html': unicode, 'speaker': unicode, 'audio_size': int,
                    'title': unicode, 'time': datetime}
    else:
        expected = {'session': str, 'preview': str, 'audio_url': str,
                    'html': str, 'speaker': str, 'audio_size': int,
                    'title': str, 'time': datetime}

    # Make sure all fields are there
    assert len(set(expected.keys()) - set(talk.keys())) == 0

    # Make sure the fields are the right type
    for key in expected:
        assert expected[key] == type(talk[key])


def test_get_all_speaker_and_count():
    """
    Do the same test as above, except use get_all_sepaker_and_count
    instead of getting individual speakers. This makes sure the database
    is correct and that the different access methods are consistent with
    each other
    """

    # Populate database
    db.clear_database()
    db.update_database(start=(2000,4), end=(2005,4))

    assert len(db.get_all_speaker_and_counts()) >= 122

    expected = {"Gordon B. Hinckley": 48,
                "Thomas S. Monson": 26,
                "Boyd K. Packer": 11,
                "L. Tom Perry": 11,
                "Joseph B. Wirthlin": 11}

    for count, speaker in db.get_all_speaker_and_counts():
        if speaker in expected:
            assert expected[speaker] == count


@pytest.mark.skipif(os.environ.get('TRAVIS') == 'true',
                    reason="Test fails on Travis because of mongodb")
def test_all_talks():
    """
    Test all talks in database up to a certain point. This will make sure
    that the database isn't changing without me knowing it.
    """

    # Populate database
    db.clear_database()
    db.update_database(end=(2015, 4))

    expected = {"Sterling W. Sill": 11,
                "Gordon B. Hinckley": 208,
                "Boyd K. Packer": 89,
                "L. Tom Perry": 87,
                "Joseph B. Wirthlin": 53,
                "Bruce R. McConkie": 27}

    for name, count in expected.items():
        talks = db.get_talk(name)
        assert len(talks) == count


def test_speakers_id():
    # Populate database
    db.clear_database()
    db.update_database(start=(2014, 4), end=(2015, 4))

    speakers_1 = ['Jeffrey R. Holland']
    speakers_2 = ['Jeffrey R. Holland', 'Henry B. Eyring']

    id_1 = db.generate_id(speakers_1)
    id_2 = db.generate_id(speakers_2)

    # Make sure I got something
    assert id_1 is not None
    assert id_2 is not None

    # Make sure ids are not the same
    assert id_1 != id_2

    # Make sure using the ID returns the same speakers
    assert len(set(db.get_speakers(id_1)) - set(speakers_1)) == 0
    assert len(set(db.get_speakers(id_2)) - set(speakers_2)) == 0

    # Make sure the id is returned again if the same speakers are used
    assert id_1 == db.generate_id(speakers_1)
    assert id_2 == db.generate_id(speakers_2)



