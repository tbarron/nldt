"""
nldt - Natural Language Date/Time support
Copyright (c) 2017 - <the end of time>  Tom Barron
See file LICENSING for details

This file contains code for testing nldt functionality.
"""
from fixtures import fx_calls_debug    # noqa
import pytest
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
    # payload
    iso = nldt.moment('01-02-03', tz='utc')
    assert iso() == '2001-02-03'
    # payload
    uso = nldt.moment('01-02-03', '%m-%d-%y')
    assert uso() == '2003-01-02'
    # payload
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
        # payload
        nldt.moment('tomorrow')
    errmsg = ("ValueError: None of the common specifications match the "
              "date/time string")
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
    Simply calling an nldt object should make it report itself in ISO format
    but without a time component
    """
    pytest.debug_func()
    now = time.time()
    exp = time.strftime("%Y-%m-%d", time.gmtime(now))
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
    exp = time.strftime(fmt, time.gmtime(now))
    wobj = nldt.moment(now)
    # payload
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
    # payload
    assert wobj.epoch() == int(now)
    # payload
    assert yesterday.epoch() == int(now - (24*3600))
    # payload
    assert tomorrow.epoch() == int(now + (24*3600))


# -----------------------------------------------------------------------------
@pytest.mark.parametrize("inp, fmt, exp", [
    pytest.param('Dec 29 2016', None, '2016-12-29', id='001'),
    pytest.param('Dec 17, 1975 03:17', '%Y-%m-%d %H:%M', '1975-12-17 03:17',
                 id='002'),
    pytest.param('2000.0704 12:35:19', '%Y-%m-%d %H:%M:%S',
                 '2000-07-04 12:35:19', id='003'),
    pytest.param('2000.0704 12:35', '%Y-%m-%d %H:%M', '2000-07-04 12:35',
                 id='iso-hm-4'),
    pytest.param('2000.0704 12', '%Y-%m-%d %H', '2000-07-04 12', id='iso-h-5'),
    pytest.param('2000.0704', None, '2000-07-04', id='default-6'),
    pytest.param('2007-07-04 17:17:17', '%Y-%m-%d %H:%M:%S',
                 '2007-07-04 17:17:17', id='iso-7'),
    pytest.param('2007-07-04 17:17', '%Y-%m-%d %H:%M', '2007-07-04 17:17',
                 id='iso-hm-8'),
    pytest.param('2007-07-04 17', '%Y-%m-%d %H', '2007-07-04 17',
                 id='iso-h-9'),
    pytest.param('2007-07-04', None, '2007-07-04', id='ymd-10'),
    pytest.param('Jul 4 2022 19:14:10', '%Y-%m-%d %H:%M:%S',
                 '2022-07-04 19:14:10', id='iso-11'),
    pytest.param('Jul 4 2022 19:14', '%Y-%m-%d %H:%M', '2022-07-04 19:14',
                 id='us-012'),
    pytest.param('Jul 4 2022 19', '%Y-%m-%d %H:%M:%S', '2022-07-04 19:00:00',
                 id='us-013'),
    pytest.param('Jul 4 2022', '%Y-%m-%d %H:%M:%S', '2022-07-04 00:00:00',
                 id='us-014'),
    pytest.param('Jul 4, 2022 19:14:10', '%Y-%m-%d %H:%M:%S',
                 '2022-07-04 19:14:10', id='us-015'),
    pytest.param('Jul 4, 2022 19:14', '%Y-%m-%d %H:%M:%S',
                 '2022-07-04 19:14:00', id='us-016'),
    pytest.param('Jul 4, 2022 19', '%Y-%m-%d %H:%M:%S', '2022-07-04 19:00:00',
                 id='us-017'),
    pytest.param('Jul 4, 2022', '%Y-%m-%d %H:%M:%S', '2022-07-04 00:00:00',
                 id='018'),
    pytest.param('4 jul 2022 19:14:10', '%Y-%m-%d %H:%M:%S',
                 '2022-07-04 19:14:10', id='019'),
    pytest.param('4 jul 2022 19:14', '%Y-%m-%d %H:%M:%S',
                 '2022-07-04 19:14:00', id='020'),
    pytest.param('4 jul 2022 19', '%Y-%m-%d %H:%M:%S', '2022-07-04 19:00:00',
                 id='021'),
    pytest.param('4 jul 2022', '%Y-%m-%d %H:%M:%S', '2022-07-04 00:00:00',
                 id='022'),
    pytest.param('4 jul, 2022 19:14:10', '%Y-%m-%d %H:%M:%S',
                 '2022-07-04 19:14:10', id='023'),
    pytest.param('4 jul, 2022 19:14', '%Y-%m-%d %H:%M:%S',
                 '2022-07-04 19:14:00', id='024'),
    pytest.param('4 jul, 2022 19', '%Y-%m-%d %H:%M:%S', '2022-07-04 19:00:00',
                 id='025'),
    pytest.param('4 jul, 2022', None, '2022-07-04', id='026'),

    pytest.param('4 July 2022 19:14:10', '%Y-%m-%d %H:%M:%S',
                 '2022-07-04 19:14:10', id='027'),
    pytest.param('4 July 2022 19:14', '%Y-%m-%d %H:%M:%S',
                 '2022-07-04 19:14:00', id='028'),
    pytest.param('4 July 2022 19', '%Y-%m-%d %H:%M:%S', '2022-07-04 19:00:00',
                 id='029'),
    pytest.param('4 July 2022', '%Y-%m-%d %H:%M:%S', '2022-07-04 00:00:00',
                 id='030'),
    pytest.param('4 July, 2022 19:14:10', '%Y-%m-%d %H:%M:%S',
                 '2022-07-04 19:14:10', id='031'),
    pytest.param('4 July, 2022 19:14', '%Y-%m-%d %H:%M:%S',
                 '2022-07-04 19:14:00', id='032'),
    pytest.param('4 July, 2022 19', '%Y-%m-%d %H:%M:%S',
                 '2022-07-04 19:00:00', id='033'),
    pytest.param('4 July, 2022', None, '2022-07-04', id='034'),
    ])
def test_intuit(inp, fmt, exp):
    """
    Try to guess popular time formats
    """
    pytest.debug_func()
    later = nldt.moment(inp, tz='utc')
    # payload
    assert later(fmt) == exp


# -----------------------------------------------------------------------------
@pytest.mark.parametrize("inp, loc, exp", [
    pytest.param('2015.0703 12:00:00', 'Pacific/Pago_Pago',
                 'Fri Jul  3 01:00:00 2015', id='Pago_Pago'),
    pytest.param('2015.0703 12:00:00', 'Pacific/Norfolk',
                 'Fri Jul  3 12:00:00 2015', id='Norfolk'),
    pytest.param('2015.0703 12:00:00', 'Universal',
                 'Fri Jul  3 12:00:00 2015', id='Universal'),
    pytest.param('2015.0703 12:00:00', 'Africa/Lusaka',
                 'Fri Jul  3 14:00:00 2015', id='Lusaka'),
    pytest.param('2015.0703 12:00:00', 'America/Adak',
                 'Fri Jul  3 03:00:00 2015', id='Adak'),
    pytest.param('2015.0703 12:00:00', 'America/Boise',
                 'Fri Jul  3 06:00:00 2015', id='Boise'),
    # pytest.param('2015.0703 12:00:00', 'Antarctica/Palmer',
    #              'Sun Jul  5 08:00:00 2015', id='Palmer'),
    pytest.param('2015.0703 12:00:00', 'Arctic/Longyearbyen',
                 'Fri Jul  3 14:00:00 2015', id='Longyearbyen'),
    pytest.param('2015.0703 12:00:00', 'Asia/Anadyr',
                 'Fri Jul  3 12:00:00 2015', id='Anadyr'),
    pytest.param('2015.0703 12:00:00', 'Asia/Kamchatka',
                 'Fri Jul  3 12:00:00 2015', id='Kamchatka'),
    # pytest.param('2015.0703 12:00:00', 'Atlantic/Stanley',
    #              'Sat Jul  4 21:00:00 2015', id='Stanley'),
    pytest.param('2015.0703 12:00:00', 'Australia/Perth',
                 'Fri Jul  3 20:00:00 2015', id='Perth'),
    # pytest.param('2015.0703 12:00:00', 'Brazil/West',
    #              'Sun Jul  5 08:00:00 2015', id='Brazil/West'),
    pytest.param('2015.0703 12:00:00', 'Canada/Atlantic',
                 'Fri Jul  3 09:00:00 2015', id='Atlantic'),
    # pytest.param('2015.0703 12:00:00', 'Chile/EasterIsland',
    #              'Mon Jul  6 06:00:00 2015', id='EasterIsland'),
    pytest.param('2015.0703 12:00:00', 'Europe/Zagreb',
                 'Fri Jul  3 14:00:00 2015', id='Zagreb'),
    pytest.param('2015.0703 12:00:00', 'Indian/Cocos',
                 'Fri Jul  3 12:00:00 2015', id='Cocos'),
    pytest.param('2015.0703 12:00:00', 'Indian/Reunion',
                 'Fri Jul  3 12:00:00 2015', id='Reunion'),
    pytest.param('2015.0703 12:00:00', 'Kwajalein',
                 'Fri Jul  3 12:00:00 2015', id='Kwajalein'),
    pytest.param('2015.0703 12:00:00', 'Pacific/Efate',
                 'Fri Jul  3 12:00:00 2015', id='Efate'),
    pytest.param('2015.0703 12:00:00', 'Pacific/Marquesas',
                 'Fri Jul  3 12:00:00 2015', id='Marquesas'),
    ])
def test_moment_asctime(inp, loc, exp):
    """
    moment.ctime() (and its alias, moment.asctime()) are both expected to
    return the utc moment in the format '%a %b %d %T %Y'. They both take the tz
    argument, which can be used to generate the return value for a specific
    timezone.
    """
    pytest.debug_func()
    this = nldt.moment(inp, tz='utc')
    assert this.asctime(tz=loc) == exp
    assert this.ctime(tz=loc) == exp


# -----------------------------------------------------------------------------
def test_moment_badattrs():
    """
    Verify that a freshly baked moment object does not have any attributes it
    should not.
    """
    pytest.debug_func()
    mobj = nldt.moment()
    assert not hasattr(mobj, 'dst')                   # payload
    assert not hasattr(mobj, 'parse')                 # payload
    assert not hasattr(mobj, 'timezone')              # payload
    assert not hasattr(mobj, 'today')                 # payload


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

    pytest.debug_func()
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
def test_moment_default_tz_pre():
    """
    Verify default tz in moment class is as expected
    """
    pytest.debug_func()
    if hasattr(nldt.moment, 'deftz'):
        del nldt.moment.deftz
    lz = get_localzone()
    assert lz.zone == nldt.moment.default_tz()


# -----------------------------------------------------------------------------
@pytest.mark.parametrize("deftz, inp, exp", [
    pytest.param("US/Eastern", "2018-01-01 12:00:00", 1514826000, id='001'),
    pytest.param("US/Central", "2018-01-01 11:00:00", 1514826000, id='002'),
    pytest.param("US/Mountain", "2018-01-01 10:00:00", 1514826000, id='003'),
    pytest.param("US/Pacific", "2018-01-01 09:00:00", 1514826000, id='004'),
    pytest.param("US/Hawaii",
                 time.struct_time((2018, 1, 1, 7, 0, 0, 0, 0, 0)),
                 1514826000, id='005'),
    pytest.param("utc", "2018-01-01 17:00:00", 1514826000, id='006'),
    pytest.param("US/Eastern", "2018-01-01 12:00:00", 1514826000, id='007'),
    ])
def test_moment_default_tz(deftz, inp, exp):
    """
    moment.default_tz() sets a default timezone to interpret input values for
    the moment constructor
    """
    pytest.debug_func()
    nldt.moment.default_tz(deftz)
    result = M(inp)
    assert result.epoch() == exp
    mexp = M(exp)
    assert result("%F %T", tz=deftz) == mexp("%F %T", tz=deftz)
    assert nldt.moment.default_tz() == deftz


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
def test_moment_gmtime():
    """
    nldt.moment.gmtime() should return the tm_struct tuple for moment.epoch()
    """
    pytest.debug_func()
    now = nldt.moment()
    exp = time.gmtime(now.epoch())
    # payload
    result = now.gmtime()
    assert result == exp


# -----------------------------------------------------------------------------
@pytest.mark.parametrize("dspec, fmt, tz, expoch", [
    pytest.param(None, None, None, "now",
                 id='001'),
    pytest.param(None, "%F %T", None,
                 nldt.InitError('moment() cannot take format or tz without '
                                'date spec'),
                 id='002'),
    pytest.param(None, None, "US/Eastern",
                 nldt.InitError('moment() cannot take format or tz without '
                                'date spec'),
                 id='003'),
    pytest.param("2018-01-01 00:00:00", "%F %T", "US/Eastern", 1514782800,
                 id='004'),
    pytest.param("2018-01-01 00:00:00", "%F %T", 'utc', 1514764800,
                 id='005'),
    pytest.param("2018.0101 01:02:03", None, "Pacific/Truk", 1514732523,
                 id='006'),
    pytest.param("2018.0704 09:23:57", None, 'utc', 1530696237,
                 id='007'),
    pytest.param((2017, 1, 1, 0, 0, 0), "%F %T", 'utc',
                 nldt.InitError("moment() cannot take format when date is not "
                                "of type str"), id='008'),
    # pytest.param(1530696573, None, 'America/Argentina/Mendoza', 1530707373,
    # id='009'),
    pytest.param(1530696573, None, None, 1530696573,
                 id='010'),
    pytest.param(time.struct_time((2010, 2, 28, 0, 32, 17, 0, 0, 0)),
                 "%F %T", None,
                 nldt.InitError('moment() cannot take format when date is not'
                                ' of type str'),
                 id='010.1'),
    pytest.param(time.struct_time((2010, 2, 28, 0, 32, 17, 0, 0, 0)),
                 None, 'utc', 1267317137,
                 id='011'),
    pytest.param(time.struct_time((2010, 2, 28, 5, 32, 17, 0, 0, 0)),
                 None, 'Europe/Stockholm', 1267331537, id='012'),
    pytest.param((2012, 2, 29, 2, 47, 19), None, None, 1330501639,
                 id='013'),
    pytest.param((2012, 2, 29, 7, 47, 19), None, 'Asia/Chongqing', 1330472839,
                 id='014'),
    pytest.param(M(14000000000), None, None, 14000000000,
                 id='015'),
    pytest.param(M(14000000000), None, 'America/Atikokan',
                 ValueError("moment(epoch) does not take timezone or format"),
                 id='016'),
    pytest.param([], None, None,
                 ValueError('Valid ways of calling nldt.moment()'),
                 id='017'),
    pytest.param([], None, 'Canada/Mountain',
                 ValueError('Valid ways of calling nldt.moment()'),
                 id='018'),
    pytest.param((1, 2, 3, 4, 5), None, None,
                 ValueError('need at least 6 values, no more than 9'),
                 id='019'),
    pytest.param((1, 2, 3, 4, 5, 6, 7, 8, 9, 10), None, None,
                 ValueError('need at least 6 values, no more than 9'),
                 id='020'),
    ])
def test_moment_init(dspec, fmt, tz, expoch):
    """
    Various combinations of arguments to moment constructor
     - no arguments => current time
    """
    pytest.debug_func()
    if expoch == "now":
        # payload
        actual = nldt.moment(dspec, fmt, tz)
        assert actual.epoch() == int(time.time())
    elif isinstance(expoch, Exception):
        with pytest.raises(type(expoch)) as err:
            # payload
            actual = nldt.moment(dspec, fmt, tz)
        assert str(expoch) in str(err.value)
    else:
        # payload
        actual = nldt.moment(dspec, fmt, tz)
        assert actual.epoch() == expoch


# -----------------------------------------------------------------------------
@pytest.mark.parametrize("inp_time, inp_tz, out_tz, out_time", [
    pytest.param('2011-01-01 00:00:00', 'utc', 'UTC', '2011-01-01 00:00:00',
                 id='001'),
    pytest.param('2011-01-01 10:00:00', 'US/Mountain', 'US/Eastern',
                 '2011-01-01 12:00:00',
                 id='002'),
    pytest.param('2011-01-01 10:00:00', 'US/Pacific', 'US/Central',
                 '2011-01-01 12:00:00',
                 id='003'),
    pytest.param('2011-01-01 17:00:00', 'Turkey', 'US/Eastern',
                 '2011-01-01 10:00:00',
                 id='004'),
    pytest.param('2004-02-28 20:00:00', 'Europe/Paris', 'Asia/Tokyo',
                 '2004-02-29 04:00:00',
                 id='005'),
    ])
def test_moment_localtime(inp_time, inp_tz, out_tz, out_time):
    """
    Test moment().localtime()
    """
    pytest.debug_func()
    expected = time.strptime(out_time, '%Y-%m-%d %H:%M:%S')
    # payload
    utc = nldt.moment(inp_time, tz=inp_tz)
    actual = utc.localtime(tz=out_tz)
    assert nldt.timegm(actual) == nldt.timegm(expected)


# -----------------------------------------------------------------------------
@pytest.mark.parametrize("minuend, subtrahend, exp", [
    pytest.param(M("2010-11-07"), D(days=3), M("2010-11-04"), id='001'),
    pytest.param(M("2008-03-05"), 5*24*3600, M("2008-02-29"), id='002'),
    pytest.param(M("2012-08-17"), M("2012-07-29"), D(days=19), id='003'),
    pytest.param(M("2015-04-28"), [1, 2, 3],
                 ValueError("Invalid subtrahend for moment subtraction"),
                 id='004'),
    ])
def test_moment_minus(minuend, subtrahend, exp):
    """
    moment - duration => moment
    moment - number-of-seconds => moment
    moment - moment => duration
    moment - list => undefined
    """
    pytest.debug_func()
    if isinstance(exp, ValueError):
        with pytest.raises(ValueError) as err:
            result = minuend - subtrahend
        assert "Invalid subtrahend for moment subtraction" in str(err)
    else:
        result = minuend - subtrahend
        assert result == exp


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
        M("2018-02-01") + [1, 2, 3]
    assert msg in str(err)


# -----------------------------------------------------------------------------
@pytest.mark.parametrize("zone", ["Africa/Freetown", "Africa/Khartoum",
                                  "America/Anchorage", "America/Glace_Bay",
                                  "Antarctica/McMurdo", "Arctic/Longyearbyen",
                                  "Asia/Dili", "Asia/Dhaka", "Asia/Amman",
                                  "Atlantic/Azores", "Atlantic/Canary",
                                  "Australia/Perth", "Australia/Canberra",
                                  "Europe/Belfast", "Europe/Moscow",
                                  "Indian/Comoro", "Indian/Christmas",
                                  "US/Eastern", "US/Pacific", "US/Central",
                                  "US/Mountain",
                                  ])
def test_moment_tz(zone):
    """
    This test verifies that a tz argument to moment.__call__() causes the UTC
    stored time to be adjusted to the time local to the passed timezone before
    display. This test verifies that a moment object can apply a timezone on
    output.
    """
    pytest.debug_func()
    now = M()
    adjusted = now.epoch() + nldt.utc_offset(tz=zone)
    expected = time.strftime("%F %T", time.gmtime(adjusted))
    # payload
    actual = now("%F %T", tz=zone)
    assert actual == expected


# -----------------------------------------------------------------------------
@pytest.mark.parametrize("inp, zone, exp", [
    pytest.param("2016.0101 00:00:00", "Africa/Freetown",
                 "2016.0101 00:00:00", id='Africa/Freetown-1'),
    pytest.param("2016.0701 00:00:00", "Africa/Freetown",
                 "2016.0701 00:00:00", id='Africa/Freetown-2'),
    pytest.param("2016.0101 00:00:00", "Africa/Khartoum",
                 "2015.1231 21:00:00", id='Africa/Khartoum-1'),
    pytest.param("2016.0701 00:00:00", "Africa/Khartoum",
                 "2016.0630 21:00:00", id='Africa/Khartoum-2'),
    pytest.param("2016.0101 00:00:00", "America/Anchorage",
                 "2016.0101 09:00:00", id='America/Anchorage'),
    pytest.param("2016.0701 00:00:00", "America/Anchorage",
                 "2016.0701 08:00:00", id='America/Anchorage'),
    pytest.param("2016.0101 00:00:00", "America/Glace_Bay",
                 "2016.0101 04:00:00", id='America/Glace_Bay'),
    pytest.param("2016.0701 00:00:00", "America/Glace_Bay",
                 "2016.0701 03:00:00", id='America/Glace_Bay'),

    pytest.param("2016.0101 00:00:00", "Antarctica/McMurdo",
                 "2015.1231 11:00:00", id='Antarctica/McMurdo'),
    pytest.param("2016.0701 00:00:00", "Antarctica/McMurdo",
                 "2016.0630 12:00:00", id='Antarctica/McMurdo'),

    pytest.param("2016.0101 00:00:00", "Arctic/Longyearbyen",
                 "2015.1231 23:00:00", id='Arctic/Longyearbyen'),
    pytest.param("2016.0701 00:00:00", "Arctic/Longyearbyen",
                 "2016.0630 22:00:00", id='Arctic/Longyearbyen'),

    pytest.param("2016.0101 00:00:00", "Asia/Dili",
                 "2015.1231 15:00:00", id='Asia/Dili'),
    pytest.param("2016.0701 00:00:00", "Asia/Dili",
                 "2016.0630 15:00:00", id='Asia/Dili'),

    pytest.param("2016.0101 00:00:00", "Asia/Dhaka",
                 "2015.1231 18:00:00", id='Asia/Dhaka'),
    pytest.param("2016.0701 00:00:00", "Asia/Dhaka",
                 "2016.0630 18:00:00", id='Asia/Dhaka'),

    pytest.param("2016.0101 00:00:00", "Asia/Amman",
                 "2015.1231 22:00:00", id='Asia/Amman'),
    pytest.param("2016.0701 00:00:00", "Asia/Amman",
                 "2016.0630 21:00:00", id='Asia/Amman'),

    pytest.param("2016.0101 00:00:00", "Atlantic/Azores",
                 "2016.0101 01:00:00", id='Atlantic/Azores'),
    pytest.param("2016.0701 00:00:00", "Atlantic/Azores",
                 "2016.0701 00:00:00", id='Atlantic/Azores'),

    pytest.param("2016.0101 00:00:00", "Atlantic/Canary",
                 "2016.0101 00:00:00", id='Atlantic/Canary'),
    pytest.param("2016.0701 00:00:00", "Atlantic/Canary",
                 "2016.0630 23:00:00", id='Atlantic/Canary'),

    pytest.param("2016.0101 00:00:00", "Australia/Perth",
                 "2015.1231 16:00:00", id='Australia/Perth'),
    pytest.param("2016.0701 00:00:00", "Australia/Perth",
                 "2016.0630 16:00:00", id='Australia/Perth'),

    pytest.param("2016.0101 00:00:00", "Australia/Canberra",
                 "2015.1231 13:00:00", id='Australia/Canberra'),
    pytest.param("2016.0701 00:00:00", "Australia/Canberra",
                 "2016.0630 14:00:00", id='Australia/Canberra'),

    pytest.param("2016.0101 00:00:00", "Europe/Belfast",
                 "2016.0101 00:00:00", id='Europe/Belfast'),
    pytest.param("2016.0701 00:00:00", "Europe/Belfast",
                 "2016.0630 23:00:00", id='Europe/Belfast'),

    pytest.param("2016.0101 00:00:00", "Europe/Moscow",
                 "2015.1231 21:00:00", id='Europe/Moscow'),
    pytest.param("2016.0701 00:00:00", "Europe/Moscow",
                 "2016.0630 21:00:00", id='Europe/Moscow'),

    pytest.param("2016.0101 00:00:00", "Indian/Comoro",
                 "2015.1231 21:00:00", id='Indian/Comoro'),
    pytest.param("2016.0701 00:00:00", "Indian/Comoro",
                 "2016.0630 21:00:00", id='Indian/Comoro'),

    pytest.param("2016.0101 00:00:00", "Indian/Christmas",
                 "2015.1231 17:00:00", id='Indian/Christmas'),
    pytest.param("2016.0701 00:00:00", "Indian/Christmas",
                 "2016.0630 17:00:00", id='Indian/Christmas'),

    pytest.param("2016.0101 00:00:00", "US/Eastern",
                 "2016.0101 05:00:00", id='US/Eastern'),
    pytest.param("2016.0701 00:00:00", "US/Eastern",
                 "2016.0701 04:00:00", id='US/Eastern'),

    pytest.param("2016.0101 00:00:00", "US/Central",
                 "2016.0101 06:00:00", id='US/Central'),
    pytest.param("2016.0701 00:00:00", "US/Central",
                 "2016.0701 05:00:00", id='US/Central'),

    pytest.param("2016.0101 00:00:00", "US/Mountain",
                 "2016.0101 07:00:00", id='US/Mountain'),
    pytest.param("2016.0701 00:00:00", "US/Mountain",
                 "2016.0701 06:00:00", id='US/Mountain'),

    pytest.param("2016.0101 00:00:00", "US/Pacific",
                 "2016.0101 08:00:00", id='US/Pacific'),
    pytest.param("2016.0701 00:00:00", "US/Pacific",
                 "2016.0701 07:00:00", id='US/Pacific'),
    ])
def test_moment_init_tz(inp, zone, exp):
    """
    Timezones when initializing a moment indicate how the input time should be
    interpreted. This test verifies that the moment constructor can apply a
    timezone on input.
    """
    pytest.debug_func()
    # payload
    when = M(inp, tz=zone)
    assert when("%Y.%m%d %T") == exp


# -----------------------------------------------------------------------------
def test_moment_time():
    """
    test.moment.time() should be an alias for test.moment.epoch()
    """
    pytest.debug_func()
    now = M()
    assert now.time() == now.epoch()


# -----------------------------------------------------------------------------
def test_repr():
    """
    The __repr__ method should provide enough info to rebuild the object
    """
    pytest.debug_func()
    c = nldt.moment()
    # payload
    assert eval(repr(c)) == c


# -----------------------------------------------------------------------------
def test_notimezone():
    """
    Moments don't have timezones -- they are strictly UTC
    """
    pytest.debug_func()
    c = nldt.moment()
    with pytest.raises(AttributeError) as err:
        # payload
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
        # payload
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
    # payload
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
    # payload
    assert str(c) == exp


# -----------------------------------------------------------------------------
def test_with_format():
    """
    If a format is specified, the spec must match
    """
    pytest.debug_func()
    wobj = nldt.moment('Dec 29, 2016', '%b %d, %Y')
    assert wobj() == '2016-12-29'
    with pytest.raises(ValueError) as err:
        # payload
        wobj = nldt.moment('Dec 29 2016', '%b %m, %Y')
    msg = "time data 'Dec 29 2016' does not match format '%b %m, %Y'"
    assert msg in str(err)


# -----------------------------------------------------------------------------
def test_with_tz():
    """
    <moment>(tz='foo') to report itself as the local time in zone 'foo'. Want
    timezones to be case insensitive.
    """
    pytest.debug_func()
    c = nldt.moment('2016-12-31 23:59:59', tz='utc')
    # assert c(tz='est') == '2016-12-31 18:59:59'
    fmt = "%Y-%m-%d %H:%M:%S"
    # payload
    assert c(fmt, tz='US/Eastern') == '2016-12-31 18:59:59'
    # payload
    assert c(fmt, tz='US/Central') == '2016-12-31 17:59:59'
    # payload
    assert c(fmt, tz='US/Mountain') == '2016-12-31 16:59:59'
    # payload
    assert c(fmt, tz='US/Pacific') == '2016-12-31 15:59:59'
    # payload
    assert c(fmt, tz='US/Hawaii') == '2016-12-31 13:59:59'
