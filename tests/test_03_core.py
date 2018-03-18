"""
nldt - Natural Language Date/Time support
Copyright (c) 2017 - <the end of time>  Tom Barron
See file LICENSING for details

This file contains code for testing nldt functionality.
"""
from fixtures import xtime
import nldt
from nldt import moment as M
from nldt import duration as D
import numbers
import pytest
import time
from nldt.text import txt
from tzlocal import get_localzone


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
    exp = xtime(fmt="%Y-%m-%d", when=now)
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
    exp = xtime(fmt=fmt, when=now)
    wobj = nldt.moment(now)
    # payload
    assert wobj(fmt) == exp


# -----------------------------------------------------------------------------
@pytest.mark.parametrize("start, end, exp", [
    pytest.param(1325242800, 1325246400, D(seconds=3600), id='001'),

    pytest.param(1325242801, (2011, 12, 30, 10, 0, 1),
                 D(seconds=-3600), id='002'),
    pytest.param(1325242802, (2011, 12, 30, 10, 0),
                 nldt.InitError('Invalid tm tuple'), id='004'),
    pytest.param(1325242803, (2011, 12, 30, 10, 0, 0, 0, 0, 0, 0),
                 nldt.InitError('Invalid tm tuple'), id='006'),

    pytest.param(1325242804,
                 time.struct_time((2011, 12, 29, 11, 0, 4, 0, 0, 0)),
                 D(days=-1), id='007'),

    pytest.param(1325242805, M('2011-12-30 11:59:59', itz='utc'),
                 D(minutes=59, seconds=54), id='008'),

    pytest.param(1325242806, '2011-12-31',
                 D(hours=12, minutes=59, seconds=54), id='009'),

    # -------------------
    pytest.param((2010, 1, 1, 0, 0, 0, 0, 0, 0), 1262323937,
                 D(hours=5, minutes=32, seconds=17), id='010'),

    pytest.param((2010, 1, 1, 0, 0, 1), (2010, 1, 2, 0, 0, 0),
                 D(hours=23, minutes=59, seconds=59), id='011'),

    pytest.param((2010, 1, 1, 0, 0, 2),
                 time.struct_time((2010, 1, 2, 0, 0, 0, 0, 0, 0)),
                 D(hours=23, minutes=59, seconds=58), id='012'),

    pytest.param((2010, 1, 1, 0, 0, 3),
                 M("2010-01-04 00:00:00", itz='utc'),
                 D(days=2, hours=23, minutes=59, seconds=57),
                 id='013'),

    pytest.param((2010, 1, 1, 0, 0, 4), "2010-01-01 00:17:00",
                 D(minutes=16, seconds=56), id='014'),

    # -------------------
    pytest.param(time.struct_time((2012, 1, 1, 0, 0, 0, 0, 0, 0)), 1325395937,
                 D(seconds=19937), id='015'),

    pytest.param(time.struct_time((2012, 1, 1, 0, 0, 1, 0, 0, 0)),
                 (2012, 1, 3, 0, 0, 1), D(days=2), id='016'),

    pytest.param(time.struct_time((2012, 1, 1, 0, 0, 2, 0, 0, 0)),
                 time.struct_time((2012, 1, 4, 0, 0, 2, 0, 0, 0)),
                 D(days=3), id='017'),

    pytest.param(time.struct_time((2012, 1, 1, 0, 0, 3, 0, 0, 0)),
                 M("2012-02-01 00:00:03", itz='utc'),
                 D(days=31),
                 id='018'),

    pytest.param(time.struct_time((2012, 1, 1, 0, 0, 4, 0, 0, 0)),
                 "2012-01-02 07:37:42", D(seconds=113858), id='019'),

    # -------------------
    pytest.param(M("2013-01-01", itz='utc'), 1357005600,
                 D(seconds=7200), id='020'),

    pytest.param(M("2013-01-01", itz='utc'), (2013, 1, 1, 2, 0, 1),
                 D(seconds=7201), id='021'),

    pytest.param(M("2013-01-01", itz='utc'),
                 time.struct_time((2013, 1, 1, 2, 0, 2, 0, 0, 0)),
                 D(seconds=7202), id='022'),

    pytest.param(M("2013-01-01"), M("2013-01-01 02:00:03"), D(seconds=7203),
                 id='023'),

    pytest.param(M("2013-01-01", itz='utc'), "2013-01-01 02:00:04",
                 D(seconds=7204), id='024'),

    # -------------------
    pytest.param("2014-01-01", 1388552400, D(seconds=18000), id='025'),

    pytest.param("2014-01-01", (2014, 1, 1, 5, 0, 1), D(seconds=18001),
                 id='026'),

    pytest.param("2014-01-01",
                 time.struct_time((2014, 1, 1, 5, 0, 2, 0, 0, 0)),
                 D(seconds=18002), id='027'),

    pytest.param("2014-01-01", M("2014-01-01 05:00:03", itz='utc'),
                 D(seconds=18003), id='028'),

    pytest.param("2014-01-01", "2014-01-01 05:00:04", D(seconds=18004),
                 id='029'),
    ])
def test_dur_start_end(start, end, exp):
    """
    Test creating a duration by difference of times in various formats (epoch,
    tuple, time.struct_time, ISO-inited moment, and bare ISO format time
    string)
    """
    pytest.debug_func()
    if isinstance(exp, Exception):
        with pytest.raises(type(exp)) as err:
            # payload
            D(end=end, start=start)
        assert str(exp) == str(err.value)
    else:
        # payload
        result = D(start=start, end=end)
        assert exp == result


# -----------------------------------------------------------------------------
@pytest.mark.parametrize("start, end, exp", [
    pytest.param(1325242800, 1325246400, D(seconds=3600), id='001'),

    pytest.param(1325242801, (2011, 12, 30, 10, 0, 1),
                 D(seconds=-3600), id='002'),
    pytest.param(1325242802, (2011, 12, 30, 10, 0),
                 ValueError('need at least 6 values, no more than 9'),
                 id='003'),
    pytest.param(1325242803, (2011, 12, 30, 10, 0, 0, 0, 0, 0, 0),
                 ValueError('need at least 6 values, no more than 9'),
                 id='004'),

    pytest.param(1325242804,
                 time.struct_time((2011, 12, 29, 11, 0, 4, 0, 0, 0)),
                 D(days=-1), id='005'),

    pytest.param(1325242805, M('2011-12-30 11:59:59', itz='utc'),
                 D(minutes=59, seconds=54), id='006'),

    pytest.param(1325242806, '2011-12-31',
                 D(hours=12, minutes=59, seconds=54), id='007'),

    # -------------------
    pytest.param((2010, 1, 1, 0, 0, 0, 0, 0, 0), 1262323937,
                 D(hours=5, minutes=32, seconds=17), id='008'),

    pytest.param((2010, 1, 1, 0, 0, 1), (2010, 1, 2, 0, 0, 0),
                 D(hours=23, minutes=59, seconds=59), id='009'),

    pytest.param((2010, 1, 1, 0, 0, 2),
                 time.struct_time((2010, 1, 2, 0, 0, 0, 0, 0, 0)),
                 D(hours=23, minutes=59, seconds=58), id='010'),

    pytest.param((2010, 1, 1, 0, 0, 3),
                 M("2010-01-04 00:00:00", itz='utc'),
                 D(days=2, hours=23, minutes=59, seconds=57), id='011'),

    pytest.param((2010, 1, 1, 0, 0, 4), "2010-01-01 00:17:00",
                 D(minutes=16, seconds=56), id='012'),

    # -------------------
    pytest.param(time.struct_time((2012, 1, 1, 0, 0, 0, 0, 0, 0)), 1325395937,
                 D(seconds=19937), id='013'),

    pytest.param(time.struct_time((2012, 1, 1, 0, 0, 1, 0, 0, 0)),
                 (2012, 1, 3, 0, 0, 1), D(days=2), id='014'),

    pytest.param(time.struct_time((2012, 1, 1, 0, 0, 2, 0, 0, 0)),
                 time.struct_time((2012, 1, 4, 0, 0, 2, 0, 0, 0)),
                 D(days=3), id='015'),

    pytest.param(time.struct_time((2012, 1, 1, 0, 0, 3, 0, 0, 0)),
                 M("2012-02-01 00:00:03", itz='utc'),
                 D(days=31), id='016'),

    pytest.param(time.struct_time((2012, 1, 1, 0, 0, 4, 0, 0, 0)),
                 "2012-01-02 07:37:42", D(seconds=113858), id='017'),

    # -------------------
    pytest.param(M("2013-01-01", itz='utc'), 1357005600,
                 D(seconds=7200), id='018'),

    pytest.param(M("2013-01-01", itz='utc'), (2013, 1, 1, 2, 0, 1),
                 D(seconds=7201), id='019'),

    pytest.param(M("2013-01-01", itz='utc'),
                 time.struct_time((2013, 1, 1, 2, 0, 2, 0, 0, 0)),
                 D(seconds=7202), id='020'),

    pytest.param(M("2013-01-01"),
                 M("2013-01-01 02:00:03"),
                 D(seconds=7203), id='021'),

    pytest.param(M("2013-01-01", itz='utc'), "2013-01-01 02:00:04",
                 D(seconds=7204), id='022'),

    # -------------------
    pytest.param("2014-01-01", 1388552400, D(seconds=18000), id='023'),

    pytest.param("2014-01-01", (2014, 1, 1, 5, 0, 1), D(seconds=18001),
                 id='024'),

    pytest.param("2014-01-01",
                 time.struct_time((2014, 1, 1, 5, 0, 2, 0, 0, 0)),
                 D(seconds=18002), id='025'),

    pytest.param("2014-01-01", M("2014-01-01 05:00:03", itz='utc'),
                 D(seconds=18003), id='026'),

    pytest.param("2014-01-01", "2014-01-01 05:00:04", D(seconds=18004),
                 id='027'),
    ])
def test_dur_moment_diff(start, end, exp):
    """
    Test creating a duration by difference of moments
    """
    pytest.debug_func()
    tz_orig = M.default_tz('utc')
    if isinstance(exp, Exception):
        with pytest.raises(type(exp)) as err:
            # payload
            M(end) - M(start)
        assert str(exp) == str(err.value)
    else:
        # payload
        result = M(end) - M(start)
        assert exp == result
    M.default_tz(tz_orig)


# -----------------------------------------------------------------------------
def test_dur_init_exc():
    """
    duration(start=...) and duration(end=...) should throw an exception
    """
    pytest.debug_func()
    with pytest.raises(nldt.InitError) as err:
        # payload
        D(start=M("2013-07-04"), years=5)
    assert "If start or end is specified, both must be" in str(err)

    with pytest.raises(nldt.InitError) as err:
        # payload
        D(end=M("2013-07-04"), years=5)
    assert "If start or end is specified, both must be" in str(err)


# -----------------------------------------------------------------------------
@pytest.mark.parametrize("y, w, d, h, m, s, x", [
    pytest.param(0, 0, 0, 0, 0, 0, D(seconds=0), id='001'),
    pytest.param(0, 0, 0, 0, 0, 6, D(seconds=6), id='002'),
    pytest.param(0, 0, 0, 0, 5, 0, D(seconds=300), id='003'),
    pytest.param(0, 0, 0, 0, 5, 6, D(seconds=306), id='004'),

    pytest.param(0, 0, 0, 4, 0, 0, D(seconds=4*3600), id='005'),
    pytest.param(0, 0, 0, 4, 0, 6, D(seconds=4*3600 + 6), id='006'),
    pytest.param(0, 0, 0, 4, 5, 0, D(seconds=4*3600 + 300), id='007'),
    pytest.param(0, 0, 0, 4, 5, 6, D(seconds=4*3600 + 306), id='008'),

    pytest.param(0, 0, 3, 0, 0, 0, D(seconds=3*24*3600), id='009'),
    pytest.param(0, 0, 3, 0, 0, 6, D(seconds=3*24*3600 + 6), id='010'),
    pytest.param(0, 0, 3, 0, 5, 0, D(seconds=3*24*3600 + 300),
                 id='011'),
    pytest.param(0, 0, 3, 0, 5, 6, D(seconds=3*24*3600 + 306),
                 id='012'),

    pytest.param(0, 0, 3, 4, 0, 0, D(seconds=76*3600), id='013'),
    pytest.param(0, 0, 3, 4, 0, 6, D(seconds=76*3600 + 6), id='014'),
    pytest.param(0, 0, 3, 4, 5, 0, D(seconds=76*3600 + 300), id='015'),
    pytest.param(0, 0, 3, 4, 5, 6, D(seconds=76*3600 + 306), id='016'),

    pytest.param(0, 2, 0, 0, 0, 0, D(seconds=14*24*3600), id='017'),
    pytest.param(0, 2, 0, 0, 0, 6, D(seconds=14*24*3600 + 6), id='018'),
    pytest.param(0, 2, 0, 0, 5, 0, D(seconds=14*24*3600 + 300),
                 id='019'),
    pytest.param(0, 2, 0, 0, 5, 6, D(seconds=14*24*3600 + 306),
                 id='020'),

    pytest.param(0, 2, 0, 4, 0, 0, D(seconds=340*3600), id='021'),
    pytest.param(0, 2, 0, 4, 0, 6, D(seconds=340*3600 + 6), id='022'),
    pytest.param(0, 2, 0, 4, 5, 0, D(seconds=340*3600 + 300), id='023'),
    pytest.param(0, 2, 0, 4, 5, 6, D(seconds=340*3600 + 306), id='024'),

    pytest.param(0, 2, 3, 0, 0, 0, D(seconds=408*3600), id='025'),
    pytest.param(0, 2, 3, 0, 0, 6, D(seconds=408*3600 + 6), id='026'),
    pytest.param(0, 2, 3, 0, 5, 0, D(seconds=408*3600 + 300), id='027'),
    pytest.param(0, 2, 3, 0, 5, 6, D(seconds=408*3600 + 306), id='028'),

    pytest.param(0, 2, 3, 4, 0, 0, D(seconds=412*3600), id='029'),
    pytest.param(0, 2, 3, 4, 0, 6, D(seconds=412*3600 + 6), id='030'),
    pytest.param(0, 2, 3, 4, 5, 0, D(seconds=412*3600 + 300), id='031'),
    pytest.param(0, 2, 3, 4, 5, 6, D(seconds=412*3600 + 306), id='032'),

    pytest.param(1, 0, 0, 0, 0, 0, D(seconds=31536000), id='033'),
    pytest.param(1, 0, 0, 0, 0, 6, D(seconds=31536000 + 6), id='034'),
    pytest.param(1, 0, 0, 0, 5, 0, D(seconds=31536000 + 300), id='035'),
    pytest.param(1, 0, 0, 0, 5, 6, D(seconds=31536000 + 306), id='036'),

    pytest.param(1, 0, 0, 4, 0, 0, D(seconds=8764*3600), id='037'),
    pytest.param(1, 0, 0, 4, 0, 6, D(seconds=8764*3600 + 6), id='038'),
    pytest.param(1, 0, 0, 4, 5, 0, D(seconds=8764*3600 + 300),
                 id='039'),
    pytest.param(1, 0, 0, 4, 5, 6, D(seconds=8764*3600 + 306),
                 id='040'),

    pytest.param(1, 0, 3, 0, 0, 0, D(seconds=368*24*3600), id='041'),
    pytest.param(1, 0, 3, 0, 0, 6, D(seconds=368*24*3600 + 6),
                 id='042'),
    pytest.param(1, 0, 3, 0, 5, 0, D(seconds=368*24*3600 + 300),
                 id='043'),
    pytest.param(1, 0, 3, 0, 5, 6, D(seconds=368*24*3600 + 306),
                 id='044'),

    pytest.param(1, 0, 3, 4, 0, 0, D(seconds=8836*3600), id='045'),
    pytest.param(1, 0, 3, 4, 0, 6, D(seconds=8836*3600 + 6), id='046'),
    pytest.param(1, 0, 3, 4, 5, 0, D(seconds=8836*3600 + 300),
                 id='047'),
    pytest.param(1, 0, 3, 4, 5, 6, D(seconds=8836*3600 + 306),
                 id='048'),

    pytest.param(1, 2, 0, 0, 0, 0, D(seconds=379*24*3600), id='049'),
    pytest.param(1, 2, 0, 0, 0, 6, D(seconds=379*24*3600 + 6),
                 id='050'),
    pytest.param(1, 2, 0, 0, 5, 0, D(seconds=379*24*3600 + 300),
                 id='051'),
    pytest.param(1, 2, 0, 0, 5, 6, D(seconds=379*24*3600 + 306),
                 id='052'),

    pytest.param(1, 2, 0, 4, 0, 0, D(seconds=9100*3600), id='053'),
    pytest.param(1, 2, 0, 4, 0, 6, D(seconds=9100*3600 + 6), id='054'),
    pytest.param(1, 2, 0, 4, 5, 0, D(seconds=9100*3600 + 300),
                 id='055'),
    pytest.param(1, 2, 0, 4, 5, 6, D(seconds=9100*3600 + 306),
                 id='056'),

    pytest.param(1, 2, 3, 0, 0, 0, D(seconds=9168*3600), id='057'),
    pytest.param(1, 2, 3, None, None, None, D(seconds=9168*3600),
                 id='058'),
    pytest.param(1, 2, 3, 0, 0, 6, D(seconds=9168*3600 + 6), id='059'),
    pytest.param(1, 2, 3, 0, 5, 0, D(seconds=9168*3600 + 300),
                 id='060'),
    pytest.param(1, 2, 3, 0, 5, 6, D(seconds=9168*3600 + 306),
                 id='061'),

    pytest.param(1, 2, 3, 4, 0, 0, D(seconds=9172*3600), id='062'),
    pytest.param(1, 2, 3, 4, 0, 6, D(seconds=9172*3600 + 6), id='063'),
    pytest.param(1, 2, 3, 4, 5, 0, D(seconds=9172*3600 + 300),
                 id='064'),
    pytest.param(1, 2, 3, 4, 5, 6, D(seconds=9172*3600 + 306),
                 id='065'),
    ])
def test_dur_ywdhms(y, w, d, h, m, s, x):
    """
    Durations can initialized by any combination of years, weeks, days, hours,
    minutes, and seconds
    """
    pytest.debug_func()
    # payload
    result = D(years=y, weeks=w, days=d, hours=h, minutes=m, seconds=s)
    assert result == x


# -----------------------------------------------------------------------------
def test_dur_add():
    """
    duration + moment-parseable => moment
    """
    pytest.debug_func()
    d = D(hours=3)
    # payload
    assert d + "2018-01-01" == M("2018-01-01 03:00:00")


# -----------------------------------------------------------------------------
def test_dur_sub_exc():
    """
    duration - not-num-dur-moment => exception
    """
    pytest.debug_func()
    d = D(hours=3)
    x = [1, 2, 3]
    with pytest.raises(TypeError) as err:
        # payload
        assert d - x
    msg = (txt['optypes-02'].format(d.__class__, x.__class__))
    assert msg in str(err)


# -----------------------------------------------------------------------------
def test_dur_repr_str():
    """
    Verify duration.__repr__, duration.__str__
    """
    pytest.debug_func()
    d = nldt.duration(years=1, weeks=2, days=3,
                      hours=4, minutes=5, seconds=6)
    # payload
    assert eval(repr(d)) == d
    # payload
    assert str(d) == '382.04:05:06'


# -----------------------------------------------------------------------------
def test_duration_dhms():
    """
    duration.dhms() reports the duration length in days.hh:mm:ss format
    """
    pytest.debug_func()
    assert D(years=1).dhms() == '365.00:00:00'
    assert D(weeks=2).dhms() == '14.00:00:00'
    assert D(days=3).dhms() == '3.00:00:00'
    assert D(hours=4).dhms() == '0.04:00:00'
    assert D(minutes=5).dhms() == '0.00:05:00'
    assert D(seconds=6).dhms() == '0.00:00:06'


# -----------------------------------------------------------------------------
@pytest.mark.parametrize("dur, fmt, exp", [
    pytest.param(D(hours=2, minutes=10, seconds=24), "%H:%M:%S",
                 "02:10:24", id='001'),
    pytest.param(D(start="2018-01-01", end="2018-01-03"), "%d.%H:%M:%S",
                 "2.00:00:00", id='002'),
    pytest.param(D(seconds=93784), "%d.%H:%M:%S", "1.02:03:04",
                 id='003'),
    pytest.param(D(seconds=26700), "%H%M", "0725", id='004'),
    pytest.param(D(start="2018-02-26", end="2018-02-25 13:00:00"),
                 "%H%M", "-1100", id='005'),
    pytest.param(D(seconds=47277), "%d.%H:%M:%S", "0.13:07:57",
                 id='006'),
    ])
def test_duration_format(dur, fmt, exp):
    """
    <duration>() -- strftime-style specifiers (where they make sense)
      %Y  Years in the time interval
      %m  not supported
      %d  days in the interval
      %H  hours in the interval
      %M  minutes in the interval
      %S  seconds in the interval
      %z  not supported
      %a  not supported
      %A  not supported
      %b  not supported
      %B  not supported
      %c  not supported
      %I  not supported
      %p  not supported
      %D  not supported
    """
    pytest.debug_func()
    # payload
    assert dur(fmt) == exp


# -----------------------------------------------------------------------------
def test_duration_minus():
    """
    duration - moment should produce exception
    """
    pytest.debug_func()
    # payload (duration - duration => duration)
    assert D(hours=1) - D(minutes=30) == D(seconds=1800)
    # payload (duration - number-of-seconds => duration)
    assert D(minutes=10) - 150 == D(seconds=450)
    with pytest.raises(TypeError) as err:
        # payload (duration - moment => exception
        assert D(seconds=25) - M("2018-02-01")
    assert txt['optypes-01'] in str(err)


# -----------------------------------------------------------------------------
def test_duration_plus():
    """
    duration + moment should produce another moment
    duration + number-of-seconds should produce another duration
    """
    pytest.debug_func()
    dur60 = D(seconds=60)
    m1 = M("2018-02-01 05:00:00")
    m2 = M("2018-02-01 05:01:00")
    # payload (duration + moment => moment)
    assert dur60 + m1 == m2
    # payload (duration + duration => duration)
    assert D(hours=1) + D(minutes=5) == D(seconds=3900)
    # payload (duration + number-of-seconds => duration)
    assert D(hours=3) + 75 == D(hours=3, minutes=1, seconds=15)


# -----------------------------------------------------------------------------
def test_duration_seconds():
    """
    duration.seconds() reports the total seconds in the duration
    """
    pytest.debug_func()
    # payload
    assert D(years=1).seconds == 365*24*3600
    # payload
    assert D(weeks=2).seconds == 14*24*3600
    # payload
    assert D(days=3).seconds == 3*24*3600
    # payload
    assert D(hours=4).seconds == 4*3600
    # payload
    assert D(minutes=5).seconds == 300
    # payload
    assert D(seconds=6).seconds == 6


# -----------------------------------------------------------------------------
def test_duration_sleep():
    """
    Test duration.sleep()
    """
    pytest.debug_func()
    nub = D(seconds=1)
    before = time.time()
    # payload
    nub.sleep()
    diff = time.time() - before
    assert abs(1.0 - diff) < 0.01


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
def test_in_local():
    """
    Verify that by default the input timezone is local
    """
    pytest.debug_func()
    tz_orig = nldt.moment.default_tz('clear')
    fixed = nldt.moment(1000000000)
    # payload -- verify default input timezone
    result = nldt.moment(fixed("%F %T", otz='local'))
    nldt.moment.default_tz(tz_orig)
    assert result.epoch() == 1000000000


# -----------------------------------------------------------------------------
def test_out_local():
    """
    Verify that by default both the input and output timezone is local
    """
    pytest.debug_func()
    zap = nldt.moment(1000000000)
    # payload -- verify default output timezone
    assert zap("%F %T", otz='local') == zap("%F %T")


# -----------------------------------------------------------------------------
@pytest.mark.parametrize("inp, fmt, exp", [
    pytest.param('Dec 29 2016', None, '2016-12-29', id='001'),
    pytest.param('Dec 17, 1975 03:17', '%Y-%m-%d %H:%M', '1975-12-17 03:17',
                 id='002'),
    pytest.param('2000.0704 12:35:19', '%Y-%m-%d %H:%M:%S',
                 '2000-07-04 12:35:19', id='003'),
    pytest.param('2000.0704 12:35', '%Y-%m-%d %H:%M', '2000-07-04 12:35',
                 id='004'),
    pytest.param('2000.0704 12', '%Y-%m-%d %H', '2000-07-04 12', id='005'),
    pytest.param('2000.0704', None, '2000-07-04', id='006'),
    pytest.param('2007-07-04 17:17:17', '%Y-%m-%d %H:%M:%S',
                 '2007-07-04 17:17:17', id='007'),
    pytest.param('2007-07-04 17:17', '%Y-%m-%d %H:%M', '2007-07-04 17:17',
                 id='008'),
    pytest.param('2007-07-04 17', '%Y-%m-%d %H', '2007-07-04 17',
                 id='009'),
    pytest.param('2007-07-04', None, '2007-07-04', id='010'),
    pytest.param('Jul 4 2022 19:14:10', '%Y-%m-%d %H:%M:%S',
                 '2022-07-04 19:14:10', id='011'),
    pytest.param('Jul 4 2022 19:14', '%Y-%m-%d %H:%M', '2022-07-04 19:14',
                 id='012'),
    pytest.param('Jul 4 2022 19', '%Y-%m-%d %H:%M:%S', '2022-07-04 19:00:00',
                 id='013'),
    pytest.param('Jul 4 2022', '%Y-%m-%d %H:%M:%S', '2022-07-04 00:00:00',
                 id='014'),
    pytest.param('Jul 4, 2022 19:14:10', '%Y-%m-%d %H:%M:%S',
                 '2022-07-04 19:14:10', id='015'),
    pytest.param('Jul 4, 2022 19:14', '%Y-%m-%d %H:%M:%S',
                 '2022-07-04 19:14:00', id='016'),
    pytest.param('Jul 4, 2022 19', '%Y-%m-%d %H:%M:%S', '2022-07-04 19:00:00',
                 id='017'),
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
    later = nldt.moment(inp, itz='local')
    # payload
    assert later(fmt) == exp


# -----------------------------------------------------------------------------
@pytest.mark.parametrize("inp, loc, exp", [
    pytest.param('2015.0703 12:00:00', 'Pacific/Pago_Pago',
                 'Fri Jul  3 01:00:00 2015', id='Pago_Pago'),
    pytest.param('2015.0703 12:00:00', 'Pacific/Norfolk',
                 'Fri Jul  3 23:00:00 2015', id='Norfolk'),
    pytest.param('2015.0703 12:00:00', 'Universal',
                 'Fri Jul  3 12:00:00 2015', id='Universal'),
    pytest.param('2015.0703 12:00:00', 'Africa/Lusaka',
                 'Fri Jul  3 14:00:00 2015', id='Lusaka'),
    pytest.param('2015.0703 12:00:00', 'America/Adak',
                 'Fri Jul  3 03:00:00 2015', id='Adak'),
    pytest.param('2015.0703 12:00:00', 'America/Boise',
                 'Fri Jul  3 06:00:00 2015', id='Boise'),
    pytest.param('2015.0703 12:00:00', 'Antarctica/Palmer',
                 'Fri Jul  3 09:00:00 2015', id='Palmer'),
    pytest.param('2015.0703 12:00:00', 'Arctic/Longyearbyen',
                 'Fri Jul  3 14:00:00 2015', id='Longyearbyen'),
    pytest.param('2015.0703 12:00:00', 'Asia/Anadyr',
                 'Sat Jul  4 00:00:00 2015', id='Anadyr'),
    pytest.param('2015.0703 12:00:00', 'Asia/Kamchatka',
                 'Sat Jul  4 00:00:00 2015', id='Kamchatka'),
    pytest.param('2015.0703 12:00:00', 'Atlantic/Stanley',
                 'Fri Jul  3 09:00:00 2015', id='Stanley'),
    pytest.param('2015.0703 12:00:00', 'Australia/Perth',
                 'Fri Jul  3 20:00:00 2015', id='Perth'),
    pytest.param('2015.0703 12:00:00', 'Brazil/West',
                 'Fri Jul  3 08:00:00 2015', id='Brazil/West'),
    pytest.param('2015.0703 12:00:00', 'Canada/Atlantic',
                 'Fri Jul  3 09:00:00 2015', id='Canada/Atlantic'),
    pytest.param('2015.0703 12:00:00', 'Chile/EasterIsland',
                 'Fri Jul  3 07:00:00 2015', id='EasterIsland'),
    pytest.param('2015.0703 12:00:00', 'Europe/Zagreb',
                 'Fri Jul  3 14:00:00 2015', id='Zagreb'),
    pytest.param('2015.0703 12:00:00', 'Indian/Cocos',
                 'Fri Jul  3 18:30:00 2015', id='Cocos'),
    pytest.param('2015.0703 12:00:00', 'Indian/Reunion',
                 'Fri Jul  3 16:00:00 2015', id='Reunion'),
    pytest.param('2015.0703 12:00:00', 'Kwajalein',
                 'Sat Jul  4 00:00:00 2015', id='Kwajalein'),
    pytest.param('2015.0703 12:00:00', 'Pacific/Efate',
                 'Fri Jul  3 23:00:00 2015', id='Efate'),
    pytest.param('2015.0703 12:00:00', 'Pacific/Marquesas',
                 'Fri Jul  3 02:30:00 2015', id='Marquesas'),
    ])
def test_moment_asctime(inp, loc, exp):
    """
    moment.ctime() (and its alias, moment.asctime()) are both expected to
    return the utc moment in the format '%a %b %d %T %Y'. They both take the tz
    argument, which can be used to generate the return value for a specific
    timezone.
    """
    pytest.debug_func()
    this = nldt.moment(inp, itz='utc')
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
            exp = nldt.timegm((tm.tm_year, tm.tm_mon,
                               tm.tm_mday + (6-tm.tm_wday),
                               23, 59, 59, 0, 0, 0))
        elif unit == 'month':
            tm = time.gmtime(now)
            maxday = nldt.month().days(year=tm.tm_year, month=tm.tm_mon)
            exp = nldt.timegm((tm.tm_year, tm.tm_mon, maxday,
                               23, 59, 59, 0, 0, 0))
        elif unit == 'year':
            tm = time.gmtime(now)
            nflr = nldt.timegm((tm.tm_year+1, 1, 1, 0, 0, 0, 0, 0, 0))
            exp = nflr - 1
        return nldt.moment(exp)

    pytest.debug_func()
    tu = nldt.time_units()
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
@pytest.mark.parametrize("this, that, exp", [
    pytest.param(M(1500000000), 1500000000, True, id='int-True'),
    pytest.param(M(1500000001), 1500000000, False, id='int-False'),
    pytest.param(M(1500000000), 1500000000.0, True, id='float-True'),
    pytest.param(M(1500000001), 1500000000.5, False, id='float-False'),
    pytest.param(M(1500000000), "1500000000", True, id='strint-True'),
    pytest.param(M(1500000001), "1500000000", False, id='strint-False'),
    pytest.param(M((2010, 1, 1, 0, 0, 0, 0, 0, 0), itz='local'),
                 time.struct_time((2010, 1, 1, 0, 0, 0, 0, 0, 0)),
                 True, id='tm-True'),
    pytest.param(M((2010, 1, 1, 0, 0, 0, 0, 0, 0), itz='local'),
                 time.struct_time((2010, 1, 1, 0, 0, 1, 0, 0, 0)),
                 False, id='tm-False'),
    pytest.param(M((2010, 1, 1, 0, 0, 0, 0, 0, 0), itz='local'),
                 (2010, 1, 1, 0, 0, 0, 0, 0, 0), True, id='tuple-True'),
    pytest.param(M((2010, 1, 1, 0, 0, 0, 0, 0, 0), itz='local'),
                 (2010, 1, 1, 0, 0, 1, 0, 0, 0), False, id='tuple-False'),

    pytest.param(M((2010, 1, 1, 0, 0, 0, 0, 0, 0), itz='local'),
                 (2010, 1, 1, 0, 0),
                 ValueError(txt['tuplen']), id='tuple-short'),
    pytest.param(M((2010, 1, 1, 0, 0, 0, 0, 0, 0), itz='local'),
                 (2010, 1, 1, 0, 0, 1, 0, 0, 0, 0),
                 ValueError(txt['tuplen']), id='tuple-long'),
    ])
def test_moment_eq(this, that, exp):
    """
    Verify that moment.__eq__() behaves as expected
    """
    pytest.debug_func()
    if isinstance(exp, Exception):
        with pytest.raises(type(exp)):
            assert (this == that)
    else:
        assert (this == that) == exp


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
            exp = nldt.timegm((tm.tm_year, tm.tm_mon, tm.tm_mday - tm.tm_wday,
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
    # ?TRAVIS
    pytest.param(xtime(fmt=txt['iso-datetime'], when=1514782800),
                 "%F %T", None, 1514782800,
                 id='local-iso'),

    pytest.param("2018.0101 01:02:03", None, "Pacific/Truk", 1514732523,
                 id='006'),
    # ?TRAVIS
    pytest.param(xtime(fmt=txt['iso-ymdhms'], when=1530710637),
                 None, None, 1530710637,
                 id='local-ymdhms'),

    pytest.param((2017, 1, 1, 0, 0, 0), "%F %T", None,
                 nldt.InitError("moment() cannot take format when date is not "
                                "of type str"), id='008'),
    pytest.param(1530696573, None, 'America/Argentina/Mendoza',
                 ValueError("moment(epoch) does not take timezone or format"),
                 id='009'),
    pytest.param(1530696573, None, None, 1530696573,
                 id='010'),
    pytest.param(time.struct_time((2010, 2, 28, 0, 32, 17, 0, 0, 0)),
                 "%F %T", None,
                 nldt.InitError('moment() cannot take format when date is not'
                                ' of type str'),
                 id='010.1'),
    # ?TRAVIS
    pytest.param(time.localtime(1267335137),
                 None, None, 1267335137,
                 id='011'),
    pytest.param(time.struct_time((2010, 2, 28, 5, 32, 17, 0, 0, 0)),
                 None, 'Europe/Stockholm', 1267331537, id='012'),
    # ?TRAVIS
    pytest.param(tuple(time.localtime(1330501639)),
                 None, None, 1330501639,
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
    utc = nldt.moment(inp_time, itz=inp_tz)
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
    msg = txt['optypes-02'].format("<class 'nldt.moment'>", "<class 'list'>")
    with pytest.raises(TypeError) as err:
        # payload
        M("2018-02-01") + [1, 2, 3]
    assert msg in str(err)


# -----------------------------------------------------------------------------
@pytest.mark.parametrize("zone", [
    pytest.param("Africa/Freetown", id='001'),
    pytest.param("Africa/Khartoum", id='002'),
    pytest.param("America/Anchorage", id='003'),
    pytest.param("America/Glace_Bay", id='004'),
    pytest.param("Antarctica/McMurdo", id='005'),
    pytest.param("Arctic/Longyearbyen", id='006'),
    pytest.param("Asia/Dili", id='007'),
    pytest.param("Asia/Dhaka", id='008'),
    pytest.param("Asia/Amman", id='009'),
    pytest.param("Atlantic/Azores", id='010'),
    pytest.param("Atlantic/Canary", id='011'),
    pytest.param("Australia/Perth", id='012'),
    pytest.param("Australia/Canberra", id='013'),
    pytest.param("Europe/Belfast", id='014'),
    pytest.param("Europe/Moscow", id='015'),
    pytest.param("Indian/Comoro", id='016'),
    pytest.param("Indian/Christmas", id='017'),
    pytest.param("US/Eastern", id='018'),
    pytest.param("US/Pacific", id='019'),
    pytest.param("US/Central", id='020'),
    pytest.param("US/Mountain", id='021'),
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
    expected = xtime(fmt="%F %T", when=adjusted, tz='utc')
    # payload
    actual = now("%F %T", otz=zone)
    assert actual == expected


# -----------------------------------------------------------------------------
@pytest.mark.parametrize("inp, inzone, exp", [
    pytest.param("2016.0101 00:00:00", "Africa/Freetown",
                 "2016.0101 00:00:00", id='001'),
    pytest.param("2016.0701 00:00:00", "Africa/Freetown",
                 "2016.0701 00:00:00", id='002'),
    pytest.param("2016.0101 00:00:00", "Africa/Khartoum",
                 "2015.1231 21:00:00", id='003'),
    pytest.param("2016.0701 00:00:00", "Africa/Khartoum",
                 "2016.0630 21:00:00", id='004'),
    pytest.param("2016.0101 00:00:00", "America/Anchorage",
                 "2016.0101 09:00:00", id='005'),
    pytest.param("2016.0701 00:00:00", "America/Anchorage",
                 "2016.0701 08:00:00", id='006'),
    pytest.param("2016.0101 00:00:00", "America/Glace_Bay",
                 "2016.0101 04:00:00", id='007'),
    pytest.param("2016.0701 00:00:00", "America/Glace_Bay",
                 "2016.0701 03:00:00", id='008'),

    pytest.param("2016.0101 00:00:00", "Antarctica/McMurdo",
                 "2015.1231 11:00:00", id='009'),
    pytest.param("2016.0701 00:00:00", "Antarctica/McMurdo",
                 "2016.0630 12:00:00", id='010'),

    pytest.param("2016.0101 00:00:00", "Arctic/Longyearbyen",
                 "2015.1231 23:00:00", id='011'),
    pytest.param("2016.0701 00:00:00", "Arctic/Longyearbyen",
                 "2016.0630 22:00:00", id='012'),

    pytest.param("2016.0101 00:00:00", "Asia/Dili",
                 "2015.1231 15:00:00", id='013'),
    pytest.param("2016.0701 00:00:00", "Asia/Dili",
                 "2016.0630 15:00:00", id='014'),

    pytest.param("2016.0101 00:00:00", "Asia/Dhaka",
                 "2015.1231 18:00:00", id='015'),
    pytest.param("2016.0701 00:00:00", "Asia/Dhaka",
                 "2016.0630 18:00:00", id='016'),

    pytest.param("2016.0101 00:00:00", "Asia/Amman",
                 "2015.1231 22:00:00", id='017'),
    pytest.param("2016.0701 00:00:00", "Asia/Amman",
                 "2016.0630 21:00:00", id='018'),

    pytest.param("2016.0101 00:00:00", "Atlantic/Azores",
                 "2016.0101 01:00:00", id='019'),
    pytest.param("2016.0701 00:00:00", "Atlantic/Azores",
                 "2016.0701 00:00:00", id='020'),

    pytest.param("2016.0101 00:00:00", "Atlantic/Canary",
                 "2016.0101 00:00:00", id='021'),
    pytest.param("2016.0701 00:00:00", "Atlantic/Canary",
                 "2016.0630 23:00:00", id='022'),

    pytest.param("2016.0101 00:00:00", "Australia/Perth",
                 "2015.1231 16:00:00", id='023'),
    pytest.param("2016.0701 00:00:00", "Australia/Perth",
                 "2016.0630 16:00:00", id='024'),

    pytest.param("2016.0101 00:00:00", "Australia/Canberra",
                 "2015.1231 13:00:00", id='025'),
    pytest.param("2016.0701 00:00:00", "Australia/Canberra",
                 "2016.0630 14:00:00", id='026'),

    pytest.param("2016.0101 00:00:00", "Europe/Belfast",
                 "2016.0101 00:00:00", id='027'),
    pytest.param("2016.0701 00:00:00", "Europe/Belfast",
                 "2016.0630 23:00:00", id='028'),

    pytest.param("2016.0101 00:00:00", "Europe/Moscow",
                 "2015.1231 21:00:00", id='029'),
    pytest.param("2016.0701 00:00:00", "Europe/Moscow",
                 "2016.0630 21:00:00", id='030'),

    pytest.param("2016.0101 00:00:00", "Indian/Comoro",
                 "2015.1231 21:00:00", id='031'),
    pytest.param("2016.0701 00:00:00", "Indian/Comoro",
                 "2016.0630 21:00:00", id='032'),

    pytest.param("2016.0101 00:00:00", "Indian/Christmas",
                 "2015.1231 17:00:00", id='033'),
    pytest.param("2016.0701 00:00:00", "Indian/Christmas",
                 "2016.0630 17:00:00", id='034'),

    pytest.param("2016.0101 00:00:00", "US/Eastern",
                 "2016.0101 05:00:00", id='035'),
    pytest.param("2016.0701 00:00:00", "US/Eastern",
                 "2016.0701 04:00:00", id='036'),

    pytest.param("2016.0101 00:00:00", "US/Central",
                 "2016.0101 06:00:00", id='037'),
    pytest.param("2016.0701 00:00:00", "US/Central",
                 "2016.0701 05:00:00", id='038'),

    pytest.param("2016.0101 00:00:00", "US/Mountain",
                 "2016.0101 07:00:00", id='039'),
    pytest.param("2016.0701 00:00:00", "US/Mountain",
                 "2016.0701 06:00:00", id='040'),

    pytest.param("2016.0101 00:00:00", "US/Pacific",
                 "2016.0101 08:00:00", id='041'),
    pytest.param("2016.0701 00:00:00", "US/Pacific",
                 "2016.0701 07:00:00", id='042'),
    ])
def test_moment_init_tz(inp, inzone, exp):
    """
    Timezones when initializing a moment indicate how the input time should be
    interpreted. This test verifies that the moment constructor can apply a
    timezone on input.
    """
    pytest.debug_func()
    # payload
    when = M(inp, itz=inzone)
    assert when("%Y.%m%d %T", otz='utc') == exp


# -----------------------------------------------------------------------------
def test_moment_time():
    """
    test.moment.time() should be an alias for test.moment.epoch()
    """
    pytest.debug_func()
    now = M()
    # payload
    assert now.time() == now.epoch()


# -----------------------------------------------------------------------------
def test_prep_init():
    """
    Verify that class prepositions instantiates properly
    """
    pytest.debug_func()
    prp = nldt.prepositions()
    assert prp.preps['of'] == 1
    assert prp.preps['in'] == 1
    assert prp.preps['from'] == 1
    assert prp.preps['after'] == 1
    assert prp.preps['before'] == -1


# -----------------------------------------------------------------------------
@pytest.mark.parametrize("inp, exp", [
    pytest.param("first of thirteenth", ("of", ["first", "of", "thirteenth"]),
                 id='001'),
    pytest.param("last week in January",
                 ("in", ["last week", "in", "January"]), id='002'),
    pytest.param("three weeks from yesterday",
                 ("from", ["three weeks", "from", "yesterday"]), id='003'),
    pytest.param("five days after tomorrow",
                 ("after", ["five days", "after", "tomorrow"]), id='004'),
    pytest.param("day before tomorrow",
                 ("before", ["day", "before", "tomorrow"]), id='005'),
    pytest.param("one two three four five",
                 (None, ["one two three four five"]), id='006'),
    ])
def test_prep_split(inp, exp):
    """
    Verify that prepositions.split() does what's expected
    """
    pytest.debug_func()
    prp = nldt.prepositions()
    assert prp.split(inp) == exp


# -----------------------------------------------------------------------------
def test_prep_are_in():
    """
    Verify that method prepositions.are_in() accurately reports whether any
    prepositions are present
    """
    pytest.debug_func()
    prp = nldt.prepositions()
    assert prp.are_in("preposition in this phrase")
    assert not prp.are_in("no prepositions here sin doff")


# -----------------------------------------------------------------------------
@pytest.mark.parametrize("inp, exp", [
    pytest.param("of", 1, id='001'),
    pytest.param("in", 1, id='002'),
    pytest.param("from", 1, id='003'),
    pytest.param("after", 1, id='004'),
    pytest.param("before", -1, id='005'),
    pytest.param("foobar", "", id='006'),
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
    assert c(fmt, otz='local') == xtime(fmt=fmt)


# -----------------------------------------------------------------------------
def test_str():
    """
    str(moment()) should report the time as UTC
    """
    pytest.debug_func()
    c = nldt.moment()
    fmt = "%Y-%m-%d %H:%M:%S"
    exp = xtime(fmt=fmt, when=c.epoch(), tz='utc')
    # payload
    assert str(c) == exp


# -----------------------------------------------------------------------------
@pytest.mark.parametrize("marg, exp", [
    pytest.param(1234123243, False, id='001'),
    pytest.param('1234123243', False, id='002'),
    pytest.param(M(1234123243), False, id='003'),
    pytest.param(time.struct_time((2018, 1, 1, 0, 0, 0, 0, 0, 0)), True,
                 id='004'),
    pytest.param((2018, 1, 1, 0, 0, 0, 0, 0, 0), True, id='005'),
    pytest.param((2018, 1, 1, 0, 0, 0, 0, 0), True, id='006'),
    pytest.param((2018, 1, 1, 0, 0, 0, 0), True, id='007'),
    pytest.param((2018, 1, 1, 0, 0, 0), True, id='008'),
    pytest.param("2018-01-01 00:00:00", True, id='009'),
    ])
def test_takes_tz(marg, exp):
    """
    Verify that nldt.moment.takes_tz() behaves as expected
    """
    pytest.debug_func()
    assert nldt.moment.takes_tz(marg) == exp


# -----------------------------------------------------------------------------
@pytest.mark.parametrize("unit, weekday, anchor, exp", [
    pytest.param('week', 'sunday', '2008.0815', '2008.0816 23:59:59',
                 id='001'),
    #                  1218758400,   1218931199
    pytest.param('week', 'monday', '2008.0815', '2008.0817 23:59:59',
                 id='002'),
    #                  1218758400,   1219017599
    pytest.param('week', 'tuesday', '2008.0815', '2008.0818 23:59:59',
                 id='003'),
    #                  1218758400,   1219103999
    pytest.param('week', 'wednesday', '2008.0815', '2008.0819 23:59:59',
                 id='004'),
    #                  1218758400,   1219190399
    pytest.param('week', 'thursday', '2008.0815', '2008.0820 23:59:59',
                 id='005'),
    #                  1218758400,   1219276799
    pytest.param('week', 'friday', '2008.0818', '2008.0821 23:59:59',
                 id='006'),
    #                  1219017600    1219363199
    pytest.param('week', 'saturday', '2008.0818', '2008.0822 23:59:59',
                 id='007'),
    #                  1219017600    1219449599

    pytest.param('minute', 'monday', '2008.1231',
                 ValueError('ceiling() only accepts start for unit=\'week\''),
                 id='010'),
    pytest.param('hour', 'monday', '2008.1231',
                 ValueError('ceiling() only accepts start for unit=\'week\''),
                 id='009'),
    pytest.param('day', 'monday', '2008.1231',
                 ValueError('ceiling() only accepts start for unit=\'week\''),
                 id='008'),
    pytest.param('week', 'frogs', '2008.1231',
                 ValueError(txt['start-inv02']), id='frogs'),
    pytest.param('month', 'monday', '2008.1231',
                 ValueError(txt['err-ceilweek']),
                 id='ceilweek'),
    pytest.param('year', 'monday', '2008.1231',
                 ValueError(txt['start-inv01']),
                 id='invalid-start'),
    ])
def test_week_ceiling_start(unit, weekday, anchor, exp):
    """
    Verify correct behavior of moment().ceiling('week', start=<weekday>) and
    that the start argument with a unit other than 'week' raises an error.
    """
    pytest.debug_func()
    tz_orig = nldt.moment.default_tz('utc')
    base = nldt.moment(anchor, itz='utc')
    if isinstance(exp, Exception):
        with pytest.raises(type(exp)):
            assert base.ceiling(unit, start=weekday) == exp
    else:
        assert base.ceiling(unit, start=weekday) == exp
    nldt.moment.default_tz(tz_orig)


# -----------------------------------------------------------------------------
@pytest.mark.parametrize("unit, weekday, anchor, exp", [
    pytest.param('week', 'sunday', '2008.0815', '2008.0810 00:00:00',
                 id='001'),
    pytest.param('week', 'monday', '2008.0815', '2008.0811 00:00:00',
                 id='002'),
    pytest.param('week', 'tuesday', '2008.0815', '2008.0812 00:00:00',
                 id='003'),
    pytest.param('week', 'wednesday', '2008.0815', '2008.0813 00:00:00',
                 id='004'),
    pytest.param('week', 'thursday', '2008.0815', '2008.0814 00:00:00',
                 id='005'),
    pytest.param('week', 'friday', '2008.0818', '2008.0815 00:00:00',
                 id='006'),
    pytest.param('week', 'saturday', '2008.0818', '2008.0816 00:00:00',
                 id='007'),

    pytest.param('day', 'monday', '2008.1231',
                 ValueError('floor() only accepts start for unit=\'week\''),
                 id='008'),
    pytest.param('hour', 'monday', '2008.1231',
                 ValueError('floor() only accepts start for unit=\'week\''),
                 id='009'),
    pytest.param('minute', 'monday', '2008.1231',
                 ValueError('floor() only accepts start for unit=\'week\''),
                 id='010'),
    pytest.param('month', 'monday', '2008.1231',
                 ValueError('floor() only accepts start for unit=\'week\''),
                 id='011'),
    pytest.param('year', 'monday', '2008.1231',
                 ValueError('floor() only accepts start for unit=\'week\''),
                 id='012'),
    ])
def test_week_floor_start(unit, weekday, anchor, exp):
    """
    Verify correct behavior of moment().floor('week', start=<weekday>) and
    moment().ceiling('week', start=<weekday>) and that the start argument with
    a unit other than 'week' raises an error.
    """
    pytest.debug_func()
    tz_orig = nldt.moment.default_tz('utc')
    base = nldt.moment(anchor, itz='utc')
    if isinstance(exp, Exception):
        with pytest.raises(type(exp)):
            assert base.floor(unit, start=weekday) == exp
    else:
        assert base.floor(unit, start=weekday) == exp
    nldt.moment.default_tz(tz_orig)


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
    assert result("%F %T", otz=deftz) == mexp("%F %T", otz=deftz)
    assert nldt.moment.default_tz() == deftz


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
def test_with_format():
    """
    If a format is specified, the spec must match
    """
    pytest.debug_func()
    wobj = nldt.moment('Dec 29, 2016', '%b %d, %Y', itz='local')
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
    c = nldt.moment('2016-12-31 23:59:59', itz='utc')
    # assert c(tz='est') == '2016-12-31 18:59:59'
    fmt = "%Y-%m-%d %H:%M:%S"
    # payload
    assert c(fmt, otz='US/Eastern') == '2016-12-31 18:59:59'
    # payload
    assert c(fmt, otz='US/Central') == '2016-12-31 17:59:59'
    # payload
    assert c(fmt, otz='US/Mountain') == '2016-12-31 16:59:59'
    # payload
    assert c(fmt, otz='US/Pacific') == '2016-12-31 15:59:59'
    # payload
    assert c(fmt, otz='US/Hawaii') == '2016-12-31 13:59:59'
