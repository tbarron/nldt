import nldt
import re
import pydoc
import pytest
import tbx


# -----------------------------------------------------------------------------
def test_flake():
    """
    Scan code for good formatting
    """
    result = tbx.run('flake8 test_nldt.py nldt')
    assert result == ''


# -----------------------------------------------------------------------------
def test_pydoc():
    """
    Verify that public items show up in pydoc output while private items do not
    """
    pytest.debug_func()
    present = ['__call__', '__eq__', '__init__', '__repr__', '__str__',
               'dst',
               'epoch',
               'localtime',
               'class moment',
               'class month',
               'class week',
               'class Parser',
               'class duration'
               ]

    absent = ['_DAY', '_end_of_day', '_end_of_month', '_end_of_week',
              '_guess_format', '_MONTHS', '_MONTH_LEN', '_nl_match',
              '_parse_return', '_WEEK', '_week_ago', '_WEEKDAYS',
              'month_index', 'month_names', 'weekday_index', 'weekday_names'
              ]

    docker = pydoc.TextDoc()
    result = re.sub("\x08.", "", docker.document(nldt))
    for item in present:
        assert item in result
    for item in absent:
        assert item not in result
