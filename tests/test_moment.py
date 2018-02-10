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


# -----------------------------------------------------------------------------
def test_ambig():
    """
    For ambiguous dates like '01-02-03' (could be Jan 2, 2003 (US order), 1 Feb
    2003 (European order), or 2001-Feb-3 (ISO order)), ISO order will be the
    default but a parse format can always be specified.
    """
    pytest.debug_func()
    iso = nldt.moment('01-02-03')
    assert iso() == '2001-02-03'
    uso = nldt.moment('01-02-03', '%m-%d-%y')
    assert uso() == '2003-01-02'
    euro = nldt.moment('01-02-03', '%d-%m-%y')
    assert euro() == '2003-02-01'


# -----------------------------------------------------------------------------
def test_arg_tomorrow():
    """
    Offset as an argument. moment('tomorrow') throws an exception.
    """
    pytest.debug_func()
    assert not hasattr(nldt, 'tomorrow')
    with pytest.raises(ValueError) as err:
        argl = nldt.moment('tomorrow')
    errmsg = "ValueError: Valid ways of calling nldt.moment():"
    assert errmsg in str(err)
    obj = nldt.moment()
    assert not hasattr(obj, 'parse')


# -----------------------------------------------------------------------------
def test_arg_yesterday():
    """
    Offset as an argument. moment('yesterday') generates the beginning of
    yesterday.
    """
    pytest.debug_func()
    assert not hasattr(nldt, 'yesterday')
    with pytest.raises(ValueError) as err:
        then = nldt.moment("yesterday")
    errmsg = "ValueError: Valid ways of calling nldt.moment():"
    assert errmsg in str(err)


# -----------------------------------------------------------------------------
def test_display():
    """
    Simply calling an nldt object should make it report itself in ISO format
    but without a time component
    """
    pytest.debug_func()
    now = time.time()
    exp = time.strftime("%Y-%m-%d", time.gmtime(now))
    wobj = nldt.moment(now)
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
    exp = time.strftime(fmt, time.gmtime(now))
    wobj = nldt.moment(now)
    assert wobj(fmt) == exp


# -----------------------------------------------------------------------------
def test_epoch():
    """
    Return the epoch form of times past, present, and future
    """
    pytest.debug_func()
    now = time.time()
    yesterday = nldt.moment(now - (24*3600))
    tomorrow = nldt.moment(now + (24*3600))
    wobj = nldt.moment(now)
    assert wobj.epoch() == int(now)
    assert yesterday.epoch() == int(now - (24*3600))
    assert tomorrow.epoch() == int(now + (24*3600))


# -----------------------------------------------------------------------------
@pytest.mark.parametrize("inp, fmt, exp",
      [('Dec 29 2016', None, '2016-12-29'),   # noqa
       ('Dec 17, 1975 03:17', '%Y-%m-%d %H:%M', '1975-12-17 03:17'),
       ('2000.0704 12:35:19', '%Y-%m-%d %H:%M:%S', '2000-07-04 12:35:19'),
       ('2000.0704 12:35', '%Y-%m-%d %H:%M', '2000-07-04 12:35'),
       ('2000.0704 12', '%Y-%m-%d %H', '2000-07-04 12'),
       ('2000.0704', None, '2000-07-04'),
       ('2007-07-04 17:17:17', '%Y-%m-%d %H:%M:%S', '2007-07-04 17:17:17'),
       ('2007-07-04 17:17', '%Y-%m-%d %H:%M', '2007-07-04 17:17'),
       ('2007-07-04 17', '%Y-%m-%d %H', '2007-07-04 17'),
       ('2007-07-04', None, '2007-07-04'),
       ('Jul 4 2022 19:14:10', '%Y-%m-%d %H:%M:%S', '2022-07-04 19:14:10'),
       ('Jul 4 2022 19:14', '%Y-%m-%d %H:%M', '2022-07-04 19:14'),
       ('Jul 4 2022 19', '%Y-%m-%d %H:%M:%S', '2022-07-04 19:00:00'),
       ('Jul 4 2022', '%Y-%m-%d %H:%M:%S', '2022-07-04 00:00:00'),
       ('Jul 4, 2022 19:14:10', '%Y-%m-%d %H:%M:%S', '2022-07-04 19:14:10'),
       ('Jul 4, 2022 19:14', '%Y-%m-%d %H:%M:%S', '2022-07-04 19:14:00'),
       ('Jul 4, 2022 19', '%Y-%m-%d %H:%M:%S', '2022-07-04 19:00:00'),
       ('Jul 4, 2022', '%Y-%m-%d %H:%M:%S', '2022-07-04 00:00:00'),
       ('4 jul 2022 19:14:10', '%Y-%m-%d %H:%M:%S', '2022-07-04 19:14:10'),
       ('4 jul 2022 19:14', '%Y-%m-%d %H:%M:%S', '2022-07-04 19:14:00'),
       ('4 jul 2022 19', '%Y-%m-%d %H:%M:%S', '2022-07-04 19:00:00'),
       ('4 jul 2022', '%Y-%m-%d %H:%M:%S', '2022-07-04 00:00:00'),
       ('4 jul, 2022 19:14:10', '%Y-%m-%d %H:%M:%S', '2022-07-04 19:14:10'),
       ('4 jul, 2022 19:14', '%Y-%m-%d %H:%M:%S', '2022-07-04 19:14:00'),
       ('4 jul, 2022 19', '%Y-%m-%d %H:%M:%S', '2022-07-04 19:00:00'),
       ('4 jul, 2022', None, '2022-07-04'),

       ('4 July 2022 19:14:10', '%Y-%m-%d %H:%M:%S', '2022-07-04 19:14:10'),
       ('4 July 2022 19:14', '%Y-%m-%d %H:%M:%S', '2022-07-04 19:14:00'),
       ('4 July 2022 19', '%Y-%m-%d %H:%M:%S', '2022-07-04 19:00:00'),
       ('4 July 2022', '%Y-%m-%d %H:%M:%S', '2022-07-04 00:00:00'),
       ('4 July, 2022 19:14:10', '%Y-%m-%d %H:%M:%S', '2022-07-04 19:14:10'),
       ('4 July, 2022 19:14', '%Y-%m-%d %H:%M:%S', '2022-07-04 19:14:00'),
       ('4 July, 2022 19', '%Y-%m-%d %H:%M:%S', '2022-07-04 19:00:00'),
       ('4 July, 2022', None, '2022-07-04'),
       ])
def test_intuit(inp, fmt, exp):
    """
    Try to guess popular time formats
    """
    pytest.debug_func()
    later = nldt.moment(inp)
    assert later(fmt) == exp


# -----------------------------------------------------------------------------
def test_moment_ceiling():
    """
    moment().ceiling(*unit*) should return the time index at the top of the
    containing *unit*. Eg., for unit 'day', the second returned should be time
    23:59:59 on the day that contains the starting moment.
    """

    def expected_ceiling(unit, now):
        if unit in ['second', 'minute', 'hour', 'day']:
            mag = tu.magnitude(unit)
            exp = now + mag - (now % mag) - 1
        elif unit == 'week':
            tm = time.gmtime(now)
            delta = wk.forediff(tm.tm_wday, 'mon')
            nflr = nldt.timegm((tm.tm_year, tm.tm_mon, tm.tm_mday + delta,
                           0, 0, 0, 0, 0, 0))
            exp = nflr - 1
        elif unit == 'month':
            tm = time.gmtime(now)
            nflr = nldt.timegm((tm.tm_year, tm.tm_mon+1, 1, 0, 0, 0, 0, 0, 0))
            exp = nflr - 1
        elif unit == 'year':
            tm = time.gmtime(now)
            nflr = nldt.timegm((tm.tm_year+1, 1, 1, 0, 0, 0, 0, 0, 0))
            exp = nflr - 1
        return nldt.moment(exp)

    tu = nldt.time_units()
    wk = nldt.week()
    now = time.time()
    mug = nldt.moment(now)
    for unit in tu.unit_list():
        # payload
        assert mug.ceiling(unit) == expected_ceiling(unit, now)

    with pytest.raises(ValueError) as err:
        # payload
        mug.ceiling('frumpy')
    assert "'frumpy' is not a time unit" in str(err)


# -----------------------------------------------------------------------------
def test_moment_floor():
    """
    moment().floor(*unit*) should return the lowest second in the indicated
    *unit* containing the starting moment. For example, floor('hour') would
    return a moment containing HH:00:00.
    """

    def expected_floor(unit, now):
        if unit in ['second', 'minute', 'hour', 'day']:
            mag = tu.magnitude(unit)
            exp = now - (now % mag)
        elif unit == 'week':
            tm = time.gmtime(now)
            delta = wk.backdiff(tm.tm_wday, 'mon') % 7
            exp = nldt.timegm((tm.tm_year, tm.tm_mon, tm.tm_mday - delta,
                          0, 0, 0, 0, 0, 0))
        elif unit == 'month':
            tm = time.gmtime(now)
            exp = nldt.timegm((tm.tm_year, tm.tm_mon, 1, 0, 0, 0, 0, 0, 0))
        elif unit == 'year':
            tm = time.gmtime(now)
            exp = nldt.timegm((tm.tm_year, 1, 1, 0, 0, 0, 0, 0, 0))
        return nldt.moment(exp)

    pytest.debug_func()
    tu = nldt.time_units()
    wk = nldt.week()
    now = time.time()
    mug = nldt.moment(now)
    for unit in tu.unit_list():
        # payload
        assert mug.floor(unit) == expected_floor(unit, now)

    with pytest.raises(ValueError) as err:
        # payload
        mug.floor('frumpy')
    assert "'frumpy' is not a time unit" in str(err)


# -----------------------------------------------------------------------------
@pytest.mark.parametrize("dspec, fmt, tz, expoch", [
    (None, None, None, "now"),
    (None, "%F %T", None,
     nldt.InitError('moment() cannot take format or tz without date spec')),
    (None, None, "US/Eastern",
     nldt.InitError('moment() cannot take format or tz without date spec')),
    ("2018-01-01 00:00:00", "%F %T", "US/Eastern", 1514782800),
    ("2018-01-01 00:00:00", "%F %T", None, 1514764800),
    ("2018.0101 01:02:03", None, "Pacific/Truk", 1514732523),
    ("2018.0704 09:23:57", None, None, 1530696237),
    ((2017, 1, 1, 0, 0, 0), "%F %T", None,
     nldt.InitError("moment() cannot take format when date is not "
                    "of type str")),
    (1530696573, None, 'America/Argentina/Mendoza', 1530707373),
    (1530696573, None, None, 1530696573),
    (time.struct_time((2010, 2, 28, 5, 32, 17, 0, 0, 0)),
     None, None, 1267335137),
    (time.struct_time((2010, 2, 28, 5, 32, 17, 0, 0, 0)),
     None, 'Europe/Stockholm', 1267331537),
    ((2012, 2, 29, 7, 47, 19), None, None, 1330501639),
    ((2012, 2, 29, 7, 47, 19), None, 'Asia/Chongqing', 1330472839),
    (M(14000000000), None, None, 14000000000),
    (M(14000000000), None, 'America/Atikokan', 14000018000),
    ([], None, None, ValueError('Valid ways of calling nldt.moment()')),
    ([], None, 'Canada/Mountain',
     ValueError('Valid ways of calling nldt.moment()')),
    ((1,2,3,4,5), None, None,
     ValueError('need at least 6 values, no more than 9')),
    ((1,2,3,4,5,6,7,8,9,10), None, None,
     ValueError('need at least 6 values, no more than 9')),
    ])
def test_moment_init(dspec, fmt, tz, expoch):
    """
    Various combinations of arguments to moment constructor
     - no arguments => current time
    """
    pytest.debug_func()
    if expoch == "now":
        actual = nldt.moment(dspec, fmt, tz)
        assert actual.epoch() == int(time.time())
    elif isinstance(expoch, Exception):
        with pytest.raises(type(expoch)) as err:
            actual = nldt.moment(dspec, fmt, tz)
        assert str(expoch) in str(err.value)
    else:
        actual = nldt.moment(dspec, fmt, tz)
        assert actual.epoch() == expoch


# -----------------------------------------------------------------------------
def test_moment_localtime():
    """
    Test moment().localtime()
    """
    now = time.time()
    foo = nldt.moment(now)
    expected = time.localtime(now)
    # payload
    actual = foo.localtime()
    assert actual == expected


# -----------------------------------------------------------------------------
def test_moment_plus():
    """
    moment + duration should produce another moment
    moment + number-of-seconds should produce another moment
    moment + list is not defined
    """
    pytest.debug_func()
    base = M("2018-02-01")
    # payload
    assert base + D(hours=3) == M("2018-02-01 03:00:00")
    # payload
    assert base + 23*3600 == M("2018-02-01 23:00:00")
    with pytest.raises(TypeError) as err:
        # payload
        assert base + M("2018-03-01") != M("2018-04-01")
    assert "sum of moments is not defined" in str(err)
    msg = ("unsupported operand type(s) for +: "
           "'<class 'nldt.moment'>' and '<class 'list'>'")
    with pytest.raises(TypeError) as err:
        # payload
        M("2018-02-01") + [1,2,3]
    assert msg in str(err)


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
def test_with_format():
    """
    If a format is specified, the spec must match
    """
    pytest.debug_func()
    wobj = nldt.moment('Dec 29, 2016', '%b %d, %Y')
    assert wobj() == '2016-12-29'
    with pytest.raises(ValueError):
        wobj = nldt.moment('Dec 29 2016', '%b %m, %Y')


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
