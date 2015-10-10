#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pytest
import rsser

def test_format_title():
    speakers = ["1", "2", "3", "4", "5"]

    assert rsser.format_title(speakers[:1]) == "1"
    assert rsser.format_title(speakers[:2]) == "1 and 2"
    assert rsser.format_title(speakers[:3]) == "1, 2, and 3"
    assert rsser.format_title(speakers[:4]) == "1, 2, 3, and 4"
    assert rsser.format_title(speakers[:5]) == "1, 2, 3, 4, and 5"
