"""
nldt - Natural Language Date/Time support
Copyright (c) 2017 - <the end of time>  Tom Barron
See file LICENSING for details

This file contains code for testing nldt functionality.
"""
from fixtures import local_formatted
import nldt
import pytest
import time
from nldt.text import txt


# -----------------------------------------------------------------------------
def test_ambig():
    """
    For ambiguous dates like '01-02-03' (could be Jan 2, 2003 (US order), 1 Feb
    2003 (European order), or 2001-Feb-3 (ISO order)), ISO order will be the
    default but a parse format can always be specified.
    """
    pytest.debug_func()
    inp = '01-02-03'
    # payload
    iso = nldt.moment(inp, itz='local')
    assert iso() == '2001-02-03'
    # payload
    uso = nldt.moment(inp, '%m-%d-%y', itz='local')
    assert uso() == '2003-01-02'
    # payload
    euro = nldt.moment(inp, '%d-%m-%y', itz='local')
    assert euro() == '2003-02-01'


# -----------------------------------------------------------------------------
def test_arg_tomorrow():
    """
    If we pass 'tomorrow' as an argument to moment(), it is expected to throw
    an exception.
    """
    pytest.debug_func()
    assert not hasattr(nldt, 'tomorrow')
    with pytest.raises(ValueError) as err:
        # payload
        nldt.moment('tomorrow')
    errmsg = "ValueError: {}".format(txt['no-match'])
    assert errmsg in str(err)


# -----------------------------------------------------------------------------
def test_arg_yesterday():
    """
    Offset as an argument. moment('yesterday') generates the beginning of
    yesterday.
    """
    pytest.debug_func()
    assert not hasattr(nldt, 'yesterday')
    with pytest.raises(ValueError) as err:
        # payload
        nldt.moment("yesterday")
    errmsg = ("ValueError: None of the common specifications match the "
              "date/time string")
    assert errmsg in str(err)


# -----------------------------------------------------------------------------
def test_display():
    """
    Simply calling an nldt.moment object should make it report itself in ISO
    format but without a time component
    """
    pytest.debug_func()
    now = time.time()
    exp = local_formatted("%Y-%m-%d", now)
    wobj = nldt.moment(now)
    # payload
    assert wobj() == exp


# -----------------------------------------------------------------------------
def test_display_formatted():
    """
    Calling an nldt object with a format should make it report itself in that
    format
    """
    pytest.debug_func()
    fmt = "%H:%M %p on %B %d, %Y"
    now = time.time()
    exp = local_formatted(fmt, now)
    wobj = nldt.moment(now)
    # payload
    assert wobj(fmt) == exp
