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
                 id='twas_brillig'),
    pytest.param('  humpty     ', ('humpty', None), id='humpty'),
    pytest.param('     ', (None, None), id='empty'),
    (['not a string'], (['not a string'], None)),
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
@pytest.mark.parametrize("inp, exp", [('one', [1]),
                                      ('two', [2]),
                                      ('three', [3]),
                                      ('four', [4]),
                                      ('five', [5]),
                                      ('six', [6]),
                                      ('seven', [7]),
                                      ('eight', [8]),
                                      ('nine', [9]),
                                      ('thirty-two', [32]),
                                      ])
def test_digits(inp, exp):
    """
    single digits
    """
    pytest.debug_func()
    assert num.scan(inp) == exp


# -----------------------------------------------------------------------------
@pytest.mark.parametrize("inp, exp", [
    pytest.param('only three weeks from now',
                 ['only', 3, 'weeks from now'],
                 id='three_weeks'),
    ('seventy-five', [75]),
    pytest.param('seventy-six trombones led the big parade',
                 [76, 'trombones led the big parade'],
                 id='trombones'),
    pytest.param("ten o'clock on june third", [10, "o'clock on june", 3],
                 id='ten-oclock'),
    pytest.param('three weeks before the fifth of may seven years ago',
                 [3, 'weeks before the', 5, 'of may', 7, 'years ago'],
                 id='three_weeks'),
    ])
def test_time_expr(inp, exp):
    """
    time expressions
    """
    pytest.debug_func()
    assert num.scan(inp) == exp
