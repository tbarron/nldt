"""
nldt - Natural Language Date/Time support
Copyright (c) 2017 - <the end of time>  Tom Barron
See file LICENSING for details

This file contains code for testing nldt functionality.
"""
from fixtures import fx_calls_debug    # noqa
from nldt import numberize as num
import pytest


# -----------------------------------------------------------------------------
@pytest.mark.parametrize("inp, exp", [
    pytest.param('   Twas brillig and the slithe toves   ',
                 ('Twas', 'brillig and the slithe toves'),
                 id='001'),
    pytest.param('  humpty     ', ('humpty', None), id='002'),
    pytest.param('     ', (None, None), id='003'),
    pytest.param(['not a string'], (['not a string'], None), id='004'),
    ])
def test_tokenize(inp, exp):
    """
    test tokenizing
    """
    pytest.debug_func()
    assert num.tokenize(inp) == exp


# -----------------------------------------------------------------------------
def test_ordinals():
    """
    Test ordinal recognition
    """
    pytest.debug_func()
    result = num.scan("first time second branch fortieth birthday "
                      "seventh crotchety thirty rock")
    assert result == [1, 'time', 2, 'branch', 40, 'birthday',
                      7, 'crotchety', 30, 'rock']


# -----------------------------------------------------------------------------
def test_scale():
    """
    Coverage for line 87-88
    """
    pytest.debug_func()
    result = num.scan("tenth ninth eighteenth two thousand "
                      "seventy-second forty-third")
    assert result == [39115]


# -----------------------------------------------------------------------------
@pytest.mark.parametrize("inp, exp", [
    pytest.param('one', [1], id='001'),
    pytest.param('two', [2], id='002'),
    pytest.param('three', [3], id='003'),
    pytest.param('four', [4], id='004'),
    pytest.param('five', [5], id='005'),
    pytest.param('six', [6], id='006'),
    pytest.param('seven', [7], id='007'),
    pytest.param('eight', [8], id='008'),
    pytest.param('nine', [9], id='009'),
    pytest.param('thirty-two', [32], id='010'),
    ])
def test_digits(inp, exp):
    """
    single digits
    """
    pytest.debug_func()
    assert num.scan(inp) == exp


# -----------------------------------------------------------------------------
@pytest.mark.parametrize("inp, exp", [
    pytest.param('only three weeks from now', ['only', 3, 'weeks from now'],
                 id='001'),
    pytest.param('seventy-five', [75], id='002'),
    pytest.param('seventy-six trombones led the big parade',
                 [76, 'trombones led the big parade'],
                 id='003'),
    pytest.param("ten o'clock on june third", [10, "o'clock on june", 3],
                 id='004'),
    pytest.param('three weeks before the fifth of may seven years ago',
                 [3, 'weeks before the', 5, 'of may', 7, 'years ago'],
                 id='005'),
    ])
def test_time_expr(inp, exp):
    """
    time expressions
    """
    pytest.debug_func()
    assert num.scan(inp) == exp
