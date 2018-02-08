import numberize
import numbers
import pydoc
import pytest
import re
import tbx
import time
import nldt
from nldt import moment as M
from nldt import duration as D
from calendar import timegm


# -----------------------------------------------------------------------------
def test_indexable_abc():
    """
    Indexable is an abstract base class that should not be instantiated
    directly.
    """
    msg = "This is an abstract base class -- don't instantiate it."
    with pytest.raises(TypeError) as err:
        _ = nldt.Indexable()
    assert msg in str(err)


# -----------------------------------------------------------------------------
@pytest.mark.parametrize("start, end, exp",
    [(1325242800, 1325246400, D(seconds=3600)),

     (1325242801, (2011, 12, 30, 10, 0, 1), D(seconds=-3600)),
     (1325242802, (2011, 12, 30, 10, 0),
      nldt.InitError('Invalid tm tuple')),
     (1325242803, (2011, 12, 30, 10, 0, 0, 0, 0, 0, 0),
      nldt.InitError('Invalid tm tuple')),

     (1325242804, time.struct_time((2011, 12, 29, 11, 0, 4, 0, 0, 0)),
      D(days=-1)),

     (1325242805, M('2011-12-30 11:59:59'), D(minutes=59, seconds=54)),

     (1325242806, '2011-12-31', D(hours=12, minutes=59, seconds=54)),

     # -------------------
     ((2010, 1, 1, 0, 0, 0, 0, 0, 0), 1262323937,
      D(hours=5, minutes=32, seconds=17)),

     ((2010, 1, 1, 0, 0, 1), (2010, 1, 2, 0, 0, 0),
      D(hours=23, minutes=59, seconds=59)),

     ((2010, 1, 1, 0, 0, 2), time.struct_time((2010, 1, 2, 0, 0, 0, 0, 0, 0)),
      D(hours=23, minutes=59, seconds=58)),

     ((2010, 1, 1, 0, 0, 3), M("2010-01-04 00:00:00"),
      D(days=2, hours=23, minutes=59, seconds=57)),

     ((2010, 1, 1, 0, 0, 4), "2010-01-01 00:17:00", D(minutes=16, seconds=56)),

     # -------------------
     (time.struct_time((2012, 1, 1, 0, 0, 0, 0, 0, 0)), 1325395937,
      D(seconds=19937)),

     (time.struct_time((2012, 1, 1, 0, 0, 1, 0, 0, 0)),
      (2012, 1, 3, 0, 0, 1), D(days=2)),

     (time.struct_time((2012, 1, 1, 0, 0, 2, 0, 0, 0)),
      time.struct_time((2012, 1, 4, 0, 0, 2, 0, 0, 0)), D(days=3)),

     (time.struct_time((2012, 1, 1, 0, 0, 3, 0, 0, 0)),
      M("2012-02-01 00:00:03"), D(days=31)),

     (time.struct_time((2012, 1, 1, 0, 0, 4, 0, 0, 0)),
      "2012-01-02 07:37:42", D(seconds=113858)),

     # -------------------
     (M("2013-01-01"), 1357005600, D(seconds=7200)),

     (M("2013-01-01"), (2013, 1, 1, 2, 0, 1), D(seconds=7201)),

     (M("2013-01-01"), time.struct_time((2013, 1, 1, 2, 0, 2, 0, 0, 0)),
      D(seconds=7202)),

     (M("2013-01-01"), M("2013-01-01 02:00:03"), D(seconds=7203)),

     (M("2013-01-01"), "2013-01-01 02:00:04", D(seconds=7204)),

     # -------------------
     ("2014-01-01", 1388552400, D(seconds=18000)),

     ("2014-01-01", (2014, 1, 1, 5, 0, 1), D(seconds=18001)),

     ("2014-01-01", time.struct_time((2014, 1, 1, 5, 0, 2, 0, 0, 0)),
      D(seconds=18002)),

     ("2014-01-01", M("2014-01-01 05:00:03"), D(seconds=18003)),

     ("2014-01-01", "2014-01-01 05:00:04", D(seconds=18004)), ])
def test_dur_start_end(start, end, exp):
    """
    Test creating a duration by difference of times
    """
    pytest.debug_func()
    if isinstance(exp, Exception):
        with pytest.raises(type(exp)) as err:
            _ = D(end=end, start=start)
        assert str(exp) == str(err.value)
    else:
        result = D(start=start, end=end)
        assert exp == result


# -----------------------------------------------------------------------------
@pytest.mark.parametrize("start, end, exp",
    [(1325242800, 1325246400, D(seconds=3600)),

     (1325242801, (2011, 12, 30, 10, 0, 1), D(seconds=-3600)),
     (1325242802, (2011, 12, 30, 10, 0),
      ValueError('need at least 6 values, no more than 9')),
     (1325242803, (2011, 12, 30, 10, 0, 0, 0, 0, 0, 0),
      ValueError('need at least 6 values, no more than 9')),

     (1325242804, time.struct_time((2011, 12, 29, 11, 0, 4, 0, 0, 0)),
      D(days=-1)),

     (1325242805, M('2011-12-30 11:59:59'), D(minutes=59, seconds=54)),

     (1325242806, '2011-12-31', D(hours=12, minutes=59, seconds=54)),

     # -------------------
     ((2010, 1, 1, 0, 0, 0, 0, 0, 0), 1262323937,
      D(hours=5, minutes=32, seconds=17)),

     ((2010, 1, 1, 0, 0, 1), (2010, 1, 2, 0, 0, 0),
      D(hours=23, minutes=59, seconds=59)),

     ((2010, 1, 1, 0, 0, 2), time.struct_time((2010, 1, 2, 0, 0, 0, 0, 0, 0)),
      D(hours=23, minutes=59, seconds=58)),

     ((2010, 1, 1, 0, 0, 3), M("2010-01-04 00:00:00"),
      D(days=2, hours=23, minutes=59, seconds=57)),

     ((2010, 1, 1, 0, 0, 4), "2010-01-01 00:17:00", D(minutes=16, seconds=56)),

     # -------------------
     (time.struct_time((2012, 1, 1, 0, 0, 0, 0, 0, 0)), 1325395937,
      D(seconds=19937)),

     (time.struct_time((2012, 1, 1, 0, 0, 1, 0, 0, 0)),
      (2012, 1, 3, 0, 0, 1), D(days=2)),

     (time.struct_time((2012, 1, 1, 0, 0, 2, 0, 0, 0)),
      time.struct_time((2012, 1, 4, 0, 0, 2, 0, 0, 0)), D(days=3)),

     (time.struct_time((2012, 1, 1, 0, 0, 3, 0, 0, 0)),
      M("2012-02-01 00:00:03"), D(days=31)),

     (time.struct_time((2012, 1, 1, 0, 0, 4, 0, 0, 0)),
      "2012-01-02 07:37:42", D(seconds=113858)),

     # -------------------
     (M("2013-01-01"), 1357005600, D(seconds=7200)),

     (M("2013-01-01"), (2013, 1, 1, 2, 0, 1), D(seconds=7201)),

     (M("2013-01-01"), time.struct_time((2013, 1, 1, 2, 0, 2, 0, 0, 0)),
      D(seconds=7202)),

     (M("2013-01-01"), M("2013-01-01 02:00:03"), D(seconds=7203)),

     (M("2013-01-01"), "2013-01-01 02:00:04", D(seconds=7204)),

     # -------------------
     ("2014-01-01", 1388552400, D(seconds=18000)),

     ("2014-01-01", (2014, 1, 1, 5, 0, 1), D(seconds=18001)),

     ("2014-01-01", time.struct_time((2014, 1, 1, 5, 0, 2, 0, 0, 0)),
      D(seconds=18002)),

     ("2014-01-01", M("2014-01-01 05:00:03"), D(seconds=18003)),

     ("2014-01-01", "2014-01-01 05:00:04", D(seconds=18004)), ])
def test_dur_moment_diff(start, end, exp):
    """
    Test creating a duration by difference of times
    """
    pytest.debug_func()
    if isinstance(exp, Exception):
        with pytest.raises(type(exp)) as err:
            _ = M(end) - M(start)
        assert str(exp) == str(err.value)
    else:
        result = M(end) - M(start)
        assert exp == result


# -----------------------------------------------------------------------------
def test_dur_init_exc():
    """
    D(start=...) and D(end=...) should throw an exception
    """
    pytest.debug_func()
    with pytest.raises(nldt.InitError) as err:
        _ = D(start=M("2013-07-04"), years=5)
    assert "If start or end is specified, both must be" in str(err)

    with pytest.raises(nldt.InitError) as err:
        _ = D(end=M("2013-07-04"), years=5)
    assert "If start or end is specified, both must be" in str(err)


# -----------------------------------------------------------------------------
@pytest.mark.parametrize("y, w, d, h, m, s, x",
                         [
    (0, 0, 0, 0, 0, 0, D(seconds=0)),
    (0, 0, 0, 0, 0, 6, D(seconds=6)),
    (0, 0, 0, 0, 5, 0, D(seconds=300)),
    (0, 0, 0, 0, 5, 6, D(seconds=306)),

    (0, 0, 0, 4, 0, 0, D(seconds=4*3600)),
    (0, 0, 0, 4, 0, 6, D(seconds=4*3600 + 6)),
    (0, 0, 0, 4, 5, 0, D(seconds=4*3600 + 300)),
    (0, 0, 0, 4, 5, 6, D(seconds=4*3600 + 306)),

    (0, 0, 3, 0, 0, 0, D(seconds=3*24*3600)),
    (0, 0, 3, 0, 0, 6, D(seconds=3*24*3600 + 6)),
    (0, 0, 3, 0, 5, 0, D(seconds=3*24*3600 + 300)),
    (0, 0, 3, 0, 5, 6, D(seconds=3*24*3600 + 306)),

    (0, 0, 3, 4, 0, 0, D(seconds=76*3600)),
    (0, 0, 3, 4, 0, 6, D(seconds=76*3600 + 6)),
    (0, 0, 3, 4, 5, 0, D(seconds=76*3600 + 300)),
    (0, 0, 3, 4, 5, 6, D(seconds=76*3600 + 306)),

    (0, 2, 0, 0, 0, 0, D(seconds=14*24*3600)),
    (0, 2, 0, 0, 0, 6, D(seconds=14*24*3600 + 6)),
    (0, 2, 0, 0, 5, 0, D(seconds=14*24*3600 + 300)),
    (0, 2, 0, 0, 5, 6, D(seconds=14*24*3600 + 306)),

    (0, 2, 0, 4, 0, 0, D(seconds=340*3600)),
    (0, 2, 0, 4, 0, 6, D(seconds=340*3600 + 6)),
    (0, 2, 0, 4, 5, 0, D(seconds=340*3600 + 300)),
    (0, 2, 0, 4, 5, 6, D(seconds=340*3600 + 306)),

    (0, 2, 3, 0, 0, 0, D(seconds=408*3600)),
    (0, 2, 3, 0, 0, 6, D(seconds=408*3600 + 6)),
    (0, 2, 3, 0, 5, 0, D(seconds=408*3600 + 300)),
    (0, 2, 3, 0, 5, 6, D(seconds=408*3600 + 306)),

    (0, 2, 3, 4, 0, 0, D(seconds=412*3600)),
    (0, 2, 3, 4, 0, 6, D(seconds=412*3600 + 6)),
    (0, 2, 3, 4, 5, 0, D(seconds=412*3600 + 300)),
    (0, 2, 3, 4, 5, 6, D(seconds=412*3600 + 306)),

    (1, 0, 0, 0, 0, 0, D(seconds=31536000)),
    (1, 0, 0, 0, 0, 6, D(seconds=31536000 + 6)),
    (1, 0, 0, 0, 5, 0, D(seconds=31536000 + 300)),
    (1, 0, 0, 0, 5, 6, D(seconds=31536000 + 306)),

    (1, 0, 0, 4, 0, 0, D(seconds=8764*3600)),
    (1, 0, 0, 4, 0, 6, D(seconds=8764*3600 + 6)),
    (1, 0, 0, 4, 5, 0, D(seconds=8764*3600 + 300)),
    (1, 0, 0, 4, 5, 6, D(seconds=8764*3600 + 306)),

    (1, 0, 3, 0, 0, 0, D(seconds=368*24*3600)),
    (1, 0, 3, 0, 0, 6, D(seconds=368*24*3600 + 6)),
    (1, 0, 3, 0, 5, 0, D(seconds=368*24*3600 + 300)),
    (1, 0, 3, 0, 5, 6, D(seconds=368*24*3600 + 306)),

    (1, 0, 3, 4, 0, 0, D(seconds=8836*3600)),
    (1, 0, 3, 4, 0, 6, D(seconds=8836*3600 + 6)),
    (1, 0, 3, 4, 5, 0, D(seconds=8836*3600 + 300)),
    (1, 0, 3, 4, 5, 6, D(seconds=8836*3600 + 306)),

    (1, 2, 0, 0, 0, 0, D(seconds=379*24*3600)),
    (1, 2, 0, 0, 0, 6, D(seconds=379*24*3600 + 6)),
    (1, 2, 0, 0, 5, 0, D(seconds=379*24*3600 + 300)),
    (1, 2, 0, 0, 5, 6, D(seconds=379*24*3600 + 306)),

    (1, 2, 0, 4, 0, 0, D(seconds=9100*3600)),
    (1, 2, 0, 4, 0, 6, D(seconds=9100*3600 + 6)),
    (1, 2, 0, 4, 5, 0, D(seconds=9100*3600 + 300)),
    (1, 2, 0, 4, 5, 6, D(seconds=9100*3600 + 306)),

    (1, 2, 3, 0, 0, 0, D(seconds=9168*3600)),
    (1, 2, 3, 0, 0, 6, D(seconds=9168*3600 + 6)),
    (1, 2, 3, 0, 5, 0, D(seconds=9168*3600 + 300)),
    (1, 2, 3, 0, 5, 6, D(seconds=9168*3600 + 306)),

    (1, 2, 3, 4, 0, 0, D(seconds=9172*3600)),
    (1, 2, 3, 4, 0, 6, D(seconds=9172*3600 + 6)),
    (1, 2, 3, 4, 5, 0, D(seconds=9172*3600 + 300)),
    (1, 2, 3, 4, 5, 6, D(seconds=9172*3600 + 306)),
    ])
def test_dur_ywdhms(y, w, d, h, m, s, x):
    """
    Durations can initialized by any combination of years, weeks, days, hours,
    minutes, and seconds
    """
    assert D(years=y, weeks=w, days=d, hours=h, minutes=m, seconds=s) == x


# -----------------------------------------------------------------------------
def test_dur_add():
    """
    duration + moment-parseable => moment
    """
    d = D(hours=3)
    assert d + "2018-01-01" == M("2018-01-01 03:00:00")
    msg = ("unsupported operand type(s) for +: "
           "'<class 'nldt.moment'>' and '<class 'list'>'")
    with pytest.raises(TypeError) as err:
        M("2018-02-01") + [1,2,3]
    assert msg in str(err)


# -----------------------------------------------------------------------------
def test_dur_sub_exc():
    """
    duration - not-num-dur-moment => exception
    """
    pytest.debug_func()
    d = D(hours=3)
    x = [1,2,3]
    with pytest.raises(TypeError) as err:
        assert d - x
    msg = ("unsupported operand type(s): '{}' and '{}'"
           .format(d.__class__, x.__class__))
    assert msg in str(err)


# -----------------------------------------------------------------------------
def test_dur_repr_str():
    """
    Verify duration.__repr__
    """
    d = nldt.duration(years=1, weeks=2, days=3,
                      hours=4, minutes=5, seconds=6)
    assert eval(repr(d)) == d
    assert str(d) == '382.04:05:06'



# -----------------------------------------------------------------------------
def test_duration_plus():
    """
    duration + moment should produce another moment
    duration + number-of-seconds should produce another duration
    """
    pytest.debug_func()
    assert D(seconds=60) + M("2018-02-01 05:00:00") == M("2018-02-01 05:01:00")
    assert D(hours=1) + D(minutes=5) == D(seconds=3900)
    assert D(hours=3) + 75 == D(hours=3, minutes=1, seconds=15)


# -----------------------------------------------------------------------------
def test_duration_minus():
    """
    duration - moment should produce exception
    """
    pytest.debug_func()
    assert D(hours=1) - D(minutes=30) == D(seconds=1800)
    assert D(minutes=10) - 150 == D(seconds=450)
    with pytest.raises(TypeError) as err:
        assert D(seconds=25) - M("2018-02-01")
    assert "unsupported operand type(s): try 'moment' - 'duration'" in str(err)


# -----------------------------------------------------------------------------
def test_month_init():
    """
    nldt.month() constructor should return an object with dict of months
    """
    pytest.debug_func()
    m = nldt.month()
    assert hasattr(m, '_dict')
    for midx in range(1, 13):
        assert midx in m._dict
    for mname in ['jan', 'feb', 'mar', 'apr', 'may', 'jun',
                  'jul', 'aug', 'sep', 'oct', 'nov', 'dec']:
        assert mname in m._dict


# -----------------------------------------------------------------------------
def test_month_index():
    """
    nldt.month_index() takes a month name and returns its index. On bad input,
    it will raise a KeyError.
    """
    m = nldt.month()
    assert m.index('jan') == 1
    assert m.index('February') == 2
    assert m.index('marc') == 3
    assert m.index('apr') == 4
    assert m.index('May') == 5
    assert m.index('june') == 6
    assert m.index('jul') == 7
    assert m.index('August') == 8
    assert m.index('sep') == 9
    assert m.index('Octob') == 10
    assert m.index('nov') == 11
    assert m.index('December') == 12
    with pytest.raises(ValueError) as err:
        assert m.index('frobble')
    assert "Could not indexify 'frobble'" in str(err)


# -----------------------------------------------------------------------------
def test_month_names():
    """
    nldt.month_names() returns the list of month names in order
    """
    m = nldt.month()
    result = m.names()
    exp = ['january', 'february', 'march', 'april', 'may', 'june',
           'july', 'august', 'september', 'october', 'november', 'december']
    assert result == exp


# -----------------------------------------------------------------------------
def test_weekday_index():
    """
    nldt.weekday_index() takes a weekday name and returns its index. On bad
    input, it will raise a KeyError.
    """
    pytest.debug_func()
    w = nldt.week()
    assert w.index('Monday') == 0
    assert w.index('tue') == 1
    assert w.index('wednesday') == 2
    assert w.index('thur') == 3
    assert w.index('fri') == 4
    assert w.index('Saturday') == 5
    assert w.index('sunda') == 6
    with pytest.raises(KeyError):
        assert w.index('foobar')


# -----------------------------------------------------------------------------
def test_weekday_names():
    """
    nldt.weekday_names() returns the list of weekday names in order
    """
    w = nldt.week()
    result = w.day_list()
    exp = ['monday', 'tuesday', 'wednesday', 'thursday',
           'friday', 'saturday', 'sunday']
    assert result == exp


# -----------------------------------------------------------------------------
def test_utc_offset():
    """
    Check routine utc_offset() against some known timezones that don't change
    with dst
    """
    assert nldt.utc_offset(tz='Singapore') == 8 * 3600

    assert nldt.utc_offset(M("2001-01-01").moment,
                           tz='Pacific/Apia') == -11 * 3600
    assert nldt.utc_offset(M("2001-07-01").moment,
                           tz='Pacific/Apia') == -11 * 3600

    assert nldt.utc_offset(M('2001-01-01').moment) == -5 * 3600
    assert nldt.utc_offset(M('2001-07-01').moment) == -4 * 3600

    tm = time.localtime()
    if tm.tm_isdst:
        assert nldt.utc_offset() == -1 * time.altzone
    else:
        assert nldt.utc_offset() == -1 * time.timezone

    with pytest.raises(TypeError) as err:
        nldt.utc_offset("not a number")
    assert "utc_offset requires an epoch time or None" in str(err)


# -----------------------------------------------------------------------------
def test_dst_now():
    """
    The module dst function should return True or False indicating whether
    Daylight Savings Time is in force or not.
    """
    pytest.debug_func()
    loc = time.localtime()
    assert nldt.dst() == (loc.tm_isdst == 1)


# -----------------------------------------------------------------------------
def test_dst_off():
    """
    The dst function should always return False for for a moment object set to
    2010-12-31 in timezone 'US/Eastern' (the local zone at the time of
    writing).
    """
    pytest.debug_func()
    then = nldt.moment("2010-12-31", "%Y-%m-%d")
    assert not hasattr(then, 'dst')
    assert not nldt.dst(then.epoch())


# -----------------------------------------------------------------------------
def test_dst_on():
    """
    The dst function should always return True for a moment object set to
    2012-07-01 in timezone 'US/Eastern' (the local zone at the time of
    writing).
    """
    pytest.debug_func()
    then = nldt.moment("2012-07-01", "%Y-%m-%d")
    assert nldt.dst(then.epoch())


# -----------------------------------------------------------------------------
def test_dst_elsewhere_off():
    """
    The dst function should return False for non local timezones that support
    DST during times of the year when DST is not in force.
    """
    pytest.debug_func()
    then = nldt.moment("2012-01-01")
    assert not nldt.dst(then.epoch(), "US/Alaska")
    assert not nldt.dst(then.epoch(), "NZ")


# -----------------------------------------------------------------------------
def test_dst_list():
    """
    """
    with pytest.raises(TypeError) as err:
        nldt.dst(time.gmtime())
    assert "dst() when arg must be str, number, or moment" in str(err)


# -----------------------------------------------------------------------------
# def test_dst_elsewhere_on():
#     """
#     The dst function should return True for non local timezones that support
#     DST during times of the year when DST IS in force.
#     """
#     pytest.debug_func()
#     then = nldt.moment("2012-07-01")
#     assert nldt.dst(then.epoch(), "US/Alaska")
#     assert nldt.dst(then.epoch(), "NZ")


# -----------------------------------------------------------------------------
def test_parse_now():
    """
    Testing nldt.Parser()
    """
    prs = nldt.Parser()
    q = M()
    then = M(time.time() - 30)
    assert prs('now') == q
    assert prs('now', q) == q
    assert prs('now', then) == then


# -----------------------------------------------------------------------------
def test_parse_tomorrow():
    """
    Calling parse with 'tomorrow' and a moment object should return a moment
    set to the following day.
    """
    pytest.debug_func()
    eoy = nldt.moment("2007-12-31")
    assert not hasattr(eoy, 'parse')
    prs = nldt.Parser()
    result = prs('tomorrow', start=eoy)
    assert result() == '2008-01-01'


# -----------------------------------------------------------------------------
def test_parse_yesterday():
    """
    Parsing 'yesterday' relative to a moment goes bacward on the calendar
    """
    pytest.debug_func()
    eoy = nldt.moment("2007-12-01")
    assert not hasattr(eoy, 'parse')
    prs = nldt.Parser()
    result = prs('yesterday', start=eoy)
    assert result() == '2007-11-30'


# -----------------------------------------------------------------------------
def test_indexify_numfloat():
    """
    Cover lines in method month.indexify()
    """
    pytest.debug_func()
    mon = nldt.month()
    assert mon.indexify(3.4) == 3


# -----------------------------------------------------------------------------
def test_indexify_numint():
    """
    Cover lines in method month.indexify()
    """
    pytest.debug_func()
    mon = nldt.month()
    assert mon.indexify(11) == 11
    with pytest.raises(ValueError) as err:
        assert mon.indexify(17) == -1
    assert "Could not indexify '17'" in str(err)


# -----------------------------------------------------------------------------
def test_indexify_numstr():
    """
    Cover lines in method month.indexify()
    """
    pytest.debug_func()
    mon = nldt.month()
    assert mon.indexify('5') == 5


# -----------------------------------------------------------------------------
def test_indexify_str():
    """
    Cover lines in method month.indexify()
    """
    pytest.debug_func()
    mon = nldt.month()
    assert mon.indexify('October') == 10


# -----------------------------------------------------------------------------
def test_indexify_lowstr():
    """
    Cover lines in method month.indexify()
    """
    pytest.debug_func()
    mon = nldt.month()
    assert mon.indexify('Oct') == 10


# -----------------------------------------------------------------------------
def test_timezone():
    """
    Timezone should return the current timezone setting
    """
    pytest.debug_func()
    if nldt.dst():
        assert nldt.timezone() == time.tzname[1]
    else:
        assert nldt.timezone() == time.tzname[0]


# -----------------------------------------------------------------------------
def nl_oracle(spec):
    """
    This function provides an oracle for tests of nldt.Parser. In this
    function, we use a simple-minded approach to find the target day. If we see
    'next', we count foward to the target day. If we see 'last', we count
    backward, without trying to do any fancy arithmetic.
    """
    wk = nldt.week()
    tu = nldt.time_units()
    prs = nldt.Parser()
    if spec == 'fourth day of this week':
        now = prs('last week')
        now = prs('next week', now)
        now = prs('next thursday', now)
        return now()
    elif spec == 'fifth day of last week':
        now = nldt.moment('last week')
        now.parse('next friday')
        return now()
    elif spec == 'today':
        return time.strftime("%Y-%m-%d", time.gmtime())
    elif spec == 'tomorrow':
        tm = time.gmtime()
        then = M(time.mktime((tm.tm_year, tm.tm_mon, tm.tm_mday+1,
                              0, 0, 0, 0, 0, 0)))
        return then()
    elif spec == 'yesterday':
        tm = time.gmtime()
        then = M(time.mktime((tm.tm_year, tm.tm_mon, tm.tm_mday-1,
                              0, 0, 0, 0, 0, 0)))
        return then()
    elif 'year' in spec:
        if nldt.word_before('year', spec) == 'next':
            year = int(time.strftime("%Y")) + 1
            return '{}-01-01'.format(year)
        elif nldt.word_before('year', spec) == 'last':
            year = int(time.strftime("%Y")) - 1
            return '{}-01-01'.format(year)
    elif 'month' in spec:
        if nldt.word_before('month', spec) == 'next':
            tm = time.gmtime()
            nmon = M(time.mktime((tm.tm_year, tm.tm_mon+1, 1,
                                  0, 0, 0, 0, 0, 0)))
            return nmon()
        elif nldt.word_before('month', spec) == 'last':
            tm = time.gmtime()
            lmon = M(time.mktime((tm.tm_year, tm.tm_mon-1, 1,
                                  0, 0, 0, 0, 0, 0)))
            return lmon()
    elif spec == 'next year':
        year = int(time.strftime("%Y")) + 1
        return '{}-01-01'.format(year)
    elif spec == 'last year':
        year = int(time.strftime("%Y")) - 1
        return '{}-01-01'.format(year)
    elif spec == 'next week':
        wdidx = wk.index('mon')
        start = prs('tomorrow')
        while wk.day_number(start) != wdidx:
            start = M(start.epoch() + tu.magnitude('day'))
        return start()
    elif spec == 'last week':
        wdidx = wk.index('mon')
        start = prs('yesterday')
        start = nldt.moment(start.epoch() - 6*24*3600)
        while wk.day_number(start) != wdidx:
            start = prs('yesterday', start)
        return start()
    elif spec == 'end of the week':
        wdidx = 6
        start = nldt.moment()
        while wk.day_number(start) != wdidx:
            start = prs('tomorrow', start)
        return start()
    elif spec == 'end of last week':
        eolw = M(nldt.moment().week_floor().epoch() - 1)
        return eolw()
    elif spec == 'beginning of next week':
        wdidx = 0
        start = prs('tomorrow')
        while wk.day_number(start) != wdidx:
            start = prs('tomorrow', start)
        return start()
    elif spec == 'first week in last January':
        wdidx = 1
        now = nldt.moment()
        year = now('%Y')
        start = nldt.moment('{}-01-07'.format(year))
        while int(start('%u')) != wdidx:
            start.parse('yesterday')
        return start()
    elif spec == 'week after next':
        nxwk = prs('next week')
        nxwk = prs('next week', nxwk)
        return nxwk()
    elif spec == 'week before last':
        lswk = prs('last week')
        lswk = prs('last week', lswk)
        return lswk()
    elif spec == 'a week ago':
        now = nldt.moment()
        then = nldt.moment(now.epoch() - 7 * 24 * 3600)
        return then()
    elif spec == 'two weeks ago':
        now = nldt.moment()
        then = nldt.moment(now.epoch() - 14 * 24 * 3600)
        return then()
    elif spec == 'three weeks from now':
        now = nldt.moment()
        then = nldt.moment(now.epoch() + 21 * 24 * 3600)
        return then()
    elif 'first week in' in spec:
        month = nldt.month()
        for mname in month.short_names():
            if mname in spec.lower():
                midx = month.index(mname)
                break
        if midx:
            now = nldt.moment()
            year = now('%Y')
            start = nldt.moment('{}-{}-07'.format(year, midx))
            while wk.day_number(start) != 0:
                start = prs('yesterday', start)
            return start()
        else:
            now = nldt.moment()
            return now()
    elif re.findall('weeks?', spec) and 'earlier' in spec:
        result = numberize.scan(spec)
        if isinstance(result[0], numbers.Number):
            mult = result[0]
        else:
            mult = 1
        now = nldt.moment()
        then = nldt.moment(now.epoch() - mult * 7 * 24 * 3600)
        return then()
    elif re.findall('weeks?', spec) and 'later' in spec:
        result = numberize.scan(spec)
        if isinstance(result[0], numbers.Number):
            mult = result[0]
        else:
            mult = 1
        now = nldt.moment()
        then = nldt.moment(now.epoch() + mult * 7 * 24 * 3600)
        return then()

    (direction, day) = spec.split()
    if direction == 'next':
        wdidx = wk.index(day)
        start = prs('tomorrow')
        while wk.day_number(start) != wdidx:
            start = M(start.epoch() + tu.magnitude('day'))
    elif direction == 'last':
        wdidx = wk.index(day)
        start = prs('yesterday')
        while wk.day_number(start) != wdidx:
            start = M(start.epoch() - tu.magnitude('day'))
    elif day == 'week':
        (day, direction) = (direction, day)
        # now direction is 'week' and day is likely a weekday (eg, 'monday
        # week')
        #
        # we've already handled '{next,last} week' above, so we don't need to
        # worry about those here
        #
        # advance to day
        wdidx = wk.index(day)
        when = prs('tomorrow')
        while wk.day_number(when) != wdidx:
            when = M(when.epoch() + tu.magnitude('day'))

        # now jump forward a week
        start = M(when.epoch() + tu.magnitude('week'))

    return start()


# -----------------------------------------------------------------------------
@pytest.mark.parametrize("inp",
                         [
                          ('last week'),
                          ('next year'),
                          ('next monday'),
                          ('next tuesday'),
                          ('next wednesday'),
                          ('next thursday'),
                          ('next friday'),
                          ('next saturday'),
                          ('next sunday'),
                          ('next week'),
                          ('next month'),
                          ('last monday'),
                          ('last tuesday'),
                          ('last wednesday'),
                          ('last thursday'),
                          ('last friday'),
                          ('last saturday'),
                          ('last sunday'),
                          ('last month'),
                          ('last year'),
                          ('today'),
                          ('tomorrow'),
                          ('yesterday'),
                          ('monday week'),
                          ('tuesday week'),
                          ('wednesday week'),
                          ('thursday week'),
                          ('friday week'),
                          ('saturday week'),
                          ('sunday week'),
                          ('end of last week'),
                          ('end of the week'),
                          ('beginning of next week'),
                          ('first week in January'),
                          ('first week in June'),
                          ('week after next'),
                          ('week before last'),
                          ('a week ago'),
                          ('three weeks from now'),
                          ('two weeks ago'),
                          ('a week earlier'),
                          ('a week later'),
                          # ('fourth day of this week'),
                          # ('fifth day of last week'),
                          # ('beginning of this week'),
                          ])
def test_natural_language(inp):
    pytest.debug_func()
    prs = nldt.Parser()
    exp = nl_oracle(inp)
    wobj = prs(inp)
    assert wobj() == exp


# -----------------------------------------------------------------------------
def test_ago_except():
    """
    Cover the ValueError exception in parse_ago
    """
    prs = nldt.Parser()
    with pytest.raises(ValueError) as err:
        prs("no number no unit ago")
    assert "No unit found in expression" in str(err)


# -----------------------------------------------------------------------------
def test_from_now_except():
    """
    Cover the ValueError exception in parse_ago
    """
    prs = nldt.Parser()
    with pytest.raises(ValueError) as err:
        prs("no number no unit from now")
    assert "No unit found in expression" in str(err)


# -----------------------------------------------------------------------------
@pytest.mark.parametrize("month, year, exp", [(1, None, 31),
                                              (2, 2017, 28),
                                              (2, 2016, 29),
                                              (2, 2000, 29),
                                              (2, 1900, 28),
                                              (3, 2018, 31),
                                              (4, None, 30),

                                              (5, None, 31),
                                              (6, None, 30),
                                              (7, None, 31),
                                              (8, None, 31),
                                              (9, None, 30),
                                              (10, None, 31),
                                              (11, None, 30),
                                              (12, None, 31),
                                              (19, None, "Could not indexify"),
                                              ])
def test_month_days(month, year, exp):
    """
    Get the number of days in each month
    """
    m = nldt.month()
    if isinstance(exp, numbers.Number):
        # payload
        assert m.days(month=month, year=year) == exp
    else:
        with pytest.raises(ValueError) as err:
            # payload
            m.days(month=month, year=year)
        assert exp in str(err)


# -----------------------------------------------------------------------------
def test_month_days_curyear():
    """
    Verify that month.days() for february this year does the right thing
    """
    mobj = nldt.month()
    now = nldt.moment()
    curyear = int(now('%Y'))
    exp = 29 if mobj.isleap(curyear) else 28
    # payload
    assert mobj.days(2) == exp


# -----------------------------------------------------------------------------
def test_isleap():
    """
    When year is not given, isleap should return True if the current year is
    leap, else False
    """
    m = nldt.month()
    if m.days(2) == 29:
        # payload
        assert m.isleap(None)
    else:
        # payload
        assert not m.isleap(None)


# -----------------------------------------------------------------------------
def test_match_monthnames():
    """
    Verify the regex returned by month.match_monthnames
    """
    m = nldt.month()
    exp = "|".join(m.names())
    exp = "(" + exp + ")"
    assert exp == m.match_monthnames()


# -----------------------------------------------------------------------------
def test_find_day():
    """
    Coverage for week.find_day
    """
    none = "No weekday name in this text"
    some = "Can you find the wednesday?"
    front = "Tuesday is a fine day"
    punct = "...Saturday we'll go to the store"
    paren = "Which day precedes (Friday) and which follows?"
    w = nldt.week()
    assert w.find_day(none) == None
    assert w.find_day(some) == "wednesday"


# -----------------------------------------------------------------------------
@pytest.mark.parametrize("inp, exp", [(0, "monday"),
                                      ("0", "monday"),
                                      ("mon", "monday"),

                                      (1, "tuesday"),
                                      ("1", "tuesday"),
                                      ("tue", "tuesday"),

                                      (2, "wednesday"),
                                      ("2", "wednesday"),
                                      ("wed", "wednesday"),

                                      (3, "thursday"),
                                      ("3", "thursday"),
                                      ("thu", "thursday"),

                                      (4, "friday"),
                                      ("4", "friday"),
                                      ("fri", "friday"),

                                      (5, "saturday"),
                                      ("5", "saturday"),
                                      ("sat", "saturday"),

                                      (6, "sunday"),
                                      ("6", "sunday"),
                                      ("sun", "sunday"),

                                      (13, "except"),
                                      ("13", "except"),
                                      ("nosuch", "except"),
                                      ])
def test_week_fullname(inp, exp):
    """
    Test week.fullname
    """
    w = nldt.week()
    if exp == "except":
        with pytest.raises(ValueError) as err:
            w.fullname(inp) == exp
        assert "Could not indexify '{}'".format(inp) in str(err)
    else:
        assert w.fullname(inp) == exp


# -----------------------------------------------------------------------------
def test_week_day_number():
    """
    Test week.day_number()
    """
    w = nldt.week()
    sat = nldt.moment("2000-01-01")
    sun = nldt.moment("2000-01-02")

    assert w.day_number(sat.epoch()) == 5
    assert w.day_number(sat) == 5

    with pytest.raises(TypeError) as err:
        # payload
        w.day_number("the other day") == 14
    assert "argument must be moment or epoch number" in str(err)

    assert w.day_number(sat, count='mon1') == 6
    assert w.day_number(sun, count='mon1') == 7

    assert w.day_number(sat, count='sun0') == 6
    assert w.day_number(sun, count='sun0') == 0


# -----------------------------------------------------------------------------
def test_prep_init():
    """
    Verify that class prepositions instantiates properly
    """
    prp = nldt.prepositions()
    assert prp.preps['of'] == 1
    assert prp.preps['in'] == 1
    assert prp.preps['from'] == 1
    assert prp.preps['after'] == 1
    assert prp.preps['before'] == -1


# -----------------------------------------------------------------------------
@pytest.mark.parametrize("inp, exp", [
    ("first of thirteenth", ("of", ["first", "of", "thirteenth"])),
    ("last week in January", ("in", ["last week", "in", "January"])),
    ("three weeks from yesterday",
     ("from", ["three weeks", "from", "yesterday"])),
    ("five days after tomorrow",
     ("after", ["five days", "after", "tomorrow"])),
    ("day before tomorrow", ("before", ["day", "before", "tomorrow"])),
    ("one two three four five", (None, ["one two three four five"])),
    ])
def test_prep_split(inp, exp):
    """
    Verify that prepositions.split() does what's expected
    """
    prp = nldt.prepositions()
    assert prp.split(inp) == exp


# -----------------------------------------------------------------------------
def test_prep_are_in():
    """
    """
    prp = nldt.prepositions()
    assert prp.are_in("preposition in this phrase")
    assert not prp.are_in("no prepositions here")


# -----------------------------------------------------------------------------
@pytest.mark.parametrize("inp, exp", [
    ("of", 1),
    ("in", 1),
    ("from", 1),
    ("after", 1),
    ("before", -1),
    ("foobar", ""),
    ])
def test_prep_direction(inp, exp):
    """
    Test for prepositions.direction()
    """
    pytest.debug_func()
    prp = nldt.prepositions()
    if isinstance(exp, numbers.Number):
        assert prp.direction(inp) == exp
    else:
        with pytest.raises(KeyError) as err:
            assert prp.direction(inp) == exp
        assert "'foobar'" in str(err)


# -----------------------------------------------------------------------------
def test_unit_list():
    """
    Verify time_units().unit_list()
    """
    tu = nldt.time_units()
    exp = ["second", "minute", "hour", "day", "week", "month", "year"]
    assert list(tu.unit_list()) == exp


# -----------------------------------------------------------------------------
def test_parser_research():
    """
    """
    prs = nldt.Parser()
    frink = "this is a string"
    with pytest.raises(TypeError) as err:
        if prs.research("boofar", "one two boofar three four", frink):
            assert frink == "this is a string"
    assert "result must be an empty list" in str(err)


# -----------------------------------------------------------------------------
def test_Stub():
    """
    The Stub class raises an exception reporting the current function that
    needs attention
    """
    with pytest.raises(nldt.Stub) as err:
        raise nldt.Stub("extra text")
    msg = "test_Stub() is a stub -- please complete it. (extra text)"
    assert msg in str(err)


# -----------------------------------------------------------------------------
def test_caller_name():
    """
    Test function caller_name()
    """
    def foobar():
        assert nldt.caller_name() == 'test_caller_name'
    foobar()
