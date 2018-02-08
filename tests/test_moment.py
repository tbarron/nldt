import numberize
import numbers
import pydoc
import pytest
import re
import tbx
import time
import nldt


# -----------------------------------------------------------------------------
# def test_bug_001():
#     """
#     nldt.moment('2016-06-07')._yesterday() is yielding '2016-06-05' when it
#     should be '2016-06-06'
#     """
#     pytest.debug_func()
#     a = nldt.moment('2016-06-07')
#     b = nldt.moment(a._yesterday())
#     assert b() == '2016-06-06'
# -----------------------------------------------------------------------------
def test_moment_plus():
    """
    moment + duration should produce another moment
    moment + number-of-seconds should produce another moment
    """
    pytest.debug_func()
    base = M("2018-02-01")
    assert base + D(hours=3) == M("2018-02-01 03:00:00")
    assert base + 23*3600 == M("2018-02-01 23:00:00")
    with pytest.raises(TypeError) as err:
        assert base + M("2018-03-01") != M("2018-04-01")
    assert "sum of moments is not defined" in str(err)


# -----------------------------------------------------------------------------
def test_repr():
    """
    The __repr__ method should provide enough info to rebuild the object
    """
    pytest.debug_func()
    c = nldt.moment()
    assert eval(repr(c)) == c


# -----------------------------------------------------------------------------
def test_notimezone():
    """
    Moments don't have timezones -- they are strictly UTC
    """
    pytest.debug_func()
    c = nldt.moment()
    with pytest.raises(AttributeError) as err:
        c.timezone()
    assert "object has no attribute 'timezone'" in str(err)


# -----------------------------------------------------------------------------
def test_nodst():
    """
    Moments don't have timezones -- they are strictly UTC
    """
    pytest.debug_func()
    c = nldt.moment()
    with pytest.raises(AttributeError) as err:
        c.dst()
    assert "object has no attribute 'dst'" in str(err)


# -----------------------------------------------------------------------------
def test_local():
    """
    Moments don't have timezones -- they are strictly UTC. However, when they
    can project themselves into the locally configured timezone.
    """
    pytest.debug_func()
    c = nldt.moment()
    fmt = "%Y.%m%d %H:%M:%S"
    assert c(fmt, tz='local') == time.strftime(fmt)


# -----------------------------------------------------------------------------
def test_str():
    """
    str(moment()) should report the time as UTC
    """
    pytest.debug_func()
    c = nldt.moment()
    fmt = "%Y-%m-%d %H:%M:%S"
    exp = time.strftime(fmt, time.gmtime(c.epoch()))
    assert str(c) == exp


# -----------------------------------------------------------------------------
def test_with_tz():
    """
    <moment>(tz='foo') to report itself as the local time in zone 'foo'. Want
    timezones to be case insensitive.
    """
    pytest.debug_func()
    c = nldt.moment('2016-12-31 23:59:59')
    # assert c(tz='est') == '2016-12-31 18:59:59'
    fmt = "%Y-%m-%d %H:%M:%S"
    assert c(fmt, tz='US/Eastern') == '2016-12-31 18:59:59'
    assert c(fmt, tz='US/Central') == '2016-12-31 17:59:59'
    assert c(fmt, tz='US/Mountain') == '2016-12-31 16:59:59'
    assert c(fmt, tz='US/Pacific') == '2016-12-31 15:59:59'
    assert c(fmt, tz='US/Hawaii') == '2016-12-31 13:59:59'
