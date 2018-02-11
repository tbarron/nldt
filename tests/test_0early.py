from fixtures import fx_calls_debug       # noqa
import nldt
import os
import pydoc
import pytest
import re
import tbx


# -----------------------------------------------------------------------------
def test_flake():
    """
    Scan code for good formatting
    """
    pytest.debug_func()
    flake_cmd = "flake8 {}".format(" ".join(pyfiles()))
    result = tbx.run(flake_cmd)
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
               'class duration',
               'class Indexable',
               'class moment',
               'class month',
               'class week',
               'class Parser',
               'class prepositions',
               'class time_units',
               'class Stub',
               'class InitError',
               ]

    absent = ['_DAY', '_end_of_day', '_end_of_month', '_end_of_week',
              '_guess_format', '_MONTHS', '_MONTH_LEN', '_nl_match',
              '_parse_return', '_WEEK', '_week_ago', '_WEEKDAYS',
              'month_index', 'month_names', 'weekday_index', 'weekday_names',
              'parse'
              ]

    docker = pydoc.TextDoc()
    result = re.sub("\x08.", "", docker.document(nldt))
    for item in present:
        assert item in result
    for item in absent:
        pattern = "\W" + item + "\W"
        assert not re.search(pattern, result)


# -----------------------------------------------------------------------------
def pyfiles():
    """
    Returns a list of .py files for this project
    """
    rval = []
    for root in ['nldt', 'tests']:
        tmpl = [os.path.join(root, x) for x in os.listdir(root)
                if x.endswith('.py')]
        rval.extend(tmpl)
    return rval
