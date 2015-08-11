#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import talk_feed as tf
import database as db
import pytest

# @pytest.fixture
# def db():
#     pass


def test_get_talk():
    talks = db.get_talk("Sterling W. Sill")
    assert len(talks) == 13

    talks = db.get_talk("Gordon B. Hinckley")
    assert len(talks) == 210


def test_get_all_speaker_and_count():
    pass
    # for i, (count, speaker) in enumerate(db.get_all_speaker_and_counts()):
    #     print(i)

