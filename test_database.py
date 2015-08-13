#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import talk_feed as tf
import database as db
import pytest
from datetime import datetime


def test_get_talk():
    # Make sure we have the most recent version
    db.update_database()

    # Pick a few speakers to make sure their counts are correct
    # I only want to pick people that aren't going to be giving
    # any more talks so their count won't change
    expected = {"Sterling W. Sill": 13,
                "Gordon B. Hinckley": 210,
                "Boyd K. Packer": 91,
                "L. Tom Perry": 87,
                "Joseph B. Wirthlin": 53,
                "Bruce R. McConkie": 29}

    for name, count in expected.items():
        talks = db.get_talk(name)
        assert len(talks) == count

    talk = db.get_talk("Gordon B. Hinckley")[0]

    # Make sure the fields that I am expecting are here
    expected = {'session': str, 'preview': str, 'audio_url': str,
                'html': str, 'speaker': str, 'audio_size': int,
                'title': str, 'time': datetime}

    assert len(set(expected.keys()) - set(talk.keys())) == 0

    # Make sure the fields are the right type
    for key in expected:
        assert expected[key] == type(talk[key])


def test_get_all_speaker_and_count():
    # Make sure we have the most recent version
    db.update_database()

    # Make sure there are the same or more talks than when I
    # wrote this test
    assert len(db.get_all_speaker_and_counts()) >= 451

    expected = {"Sterling W. Sill": 13,
                "Gordon B. Hinckley": 210,
                "Boyd K. Packer": 91,
                "L. Tom Perry": 87,
                "Joseph B. Wirthlin": 53,
                "Bruce R. McConkie": 29}

    # Make sure the counts are the same
    # This tests the same thing as the previous tests
    # This makes sure the database is correct and that the methods
    # are consistent with each other
    for count, speaker in db.get_all_speaker_and_counts():
        if speaker in expected:
            assert expected[speaker] == count


def test_speakers_id():
    # Make sure we have the most recent version
    db.update_database()

    speakers = ['Jeffrey R. Holland']
    id_ = db.generate_id(speakers)

    # Make sure I got something
    assert id_ is not None

    # Make sure using the ID returns the same speakers
    assert db.get_speakers(id_) == speakers

    # Make sure the id is returned again if the same speakers are used
    assert id_ == db.generate_id(speakers)


