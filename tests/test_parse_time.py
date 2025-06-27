import pytest
from agegrader.agegrader import parse_time

def test_parse_hms():
    parsed = parse_time('1:08:20')
    assert parsed == 3600 + 8 * 60 + 20

def test_parse_hms_zero_h():
    parsed = parse_time('0:08:20')
    assert parsed == 8 * 60 + 20

def test_parse_ms():
    parsed = parse_time('08:20')
    assert parsed == 8 * 60 + 20