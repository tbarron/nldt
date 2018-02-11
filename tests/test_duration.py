from fixtures import fx_calls_debug    # noqa
import nldt
from nldt import moment
from nldt import duration
import pytest
import time


# -----------------------------------------------------------------------------
@pytest.mark.parametrize("start, end, exp", [
    (1325242800, 1325246400, duration(seconds=3600)),

    (1325242801, (2011, 12, 30, 10, 0, 1), duration(seconds=-3600)),
    (1325242802, (2011, 12, 30, 10, 0),
     nldt.InitError('Invalid tm tuple')),
    (1325242803, (2011, 12, 30, 10, 0, 0, 0, 0, 0, 0),
     nldt.InitError('Invalid tm tuple')),

    (1325242804, time.struct_time((2011, 12, 29, 11, 0, 4, 0, 0, 0)),
     duration(days=-1)),

    (1325242805, moment('2011-12-30 11:59:59'),
     duration(minutes=59, seconds=54)),

    (1325242806, '2011-12-31', duration(hours=12, minutes=59, seconds=54)),

    # -------------------
    ((2010, 1, 1, 0, 0, 0, 0, 0, 0), 1262323937,
     duration(hours=5, minutes=32, seconds=17)),

    ((2010, 1, 1, 0, 0, 1), (2010, 1, 2, 0, 0, 0),
     duration(hours=23, minutes=59, seconds=59)),

    ((2010, 1, 1, 0, 0, 2), time.struct_time((2010, 1, 2, 0, 0, 0, 0, 0, 0)),
     duration(hours=23, minutes=59, seconds=58)),

    ((2010, 1, 1, 0, 0, 3), moment("2010-01-04 00:00:00"),
     duration(days=2, hours=23, minutes=59, seconds=57)),

    ((2010, 1, 1, 0, 0, 4), "2010-01-01 00:17:00",
     duration(minutes=16, seconds=56)),

    # -------------------
    (time.struct_time((2012, 1, 1, 0, 0, 0, 0, 0, 0)), 1325395937,
     duration(seconds=19937)),

    (time.struct_time((2012, 1, 1, 0, 0, 1, 0, 0, 0)),
     (2012, 1, 3, 0, 0, 1), duration(days=2)),

    (time.struct_time((2012, 1, 1, 0, 0, 2, 0, 0, 0)),
     time.struct_time((2012, 1, 4, 0, 0, 2, 0, 0, 0)), duration(days=3)),

    (time.struct_time((2012, 1, 1, 0, 0, 3, 0, 0, 0)),
     moment("2012-02-01 00:00:03"), duration(days=31)),

    (time.struct_time((2012, 1, 1, 0, 0, 4, 0, 0, 0)),
     "2012-01-02 07:37:42", duration(seconds=113858)),

    # -------------------
    (moment("2013-01-01"), 1357005600, duration(seconds=7200)),

    (moment("2013-01-01"), (2013, 1, 1, 2, 0, 1), duration(seconds=7201)),

    (moment("2013-01-01"), time.struct_time((2013, 1, 1, 2, 0, 2, 0, 0, 0)),
     duration(seconds=7202)),

    (moment("2013-01-01"), moment("2013-01-01 02:00:03"),
     duration(seconds=7203)),

    (moment("2013-01-01"), "2013-01-01 02:00:04", duration(seconds=7204)),

    # -------------------
    ("2014-01-01", 1388552400, duration(seconds=18000)),

    ("2014-01-01", (2014, 1, 1, 5, 0, 1), duration(seconds=18001)),

    ("2014-01-01", time.struct_time((2014, 1, 1, 5, 0, 2, 0, 0, 0)),
     duration(seconds=18002)),

    ("2014-01-01", moment("2014-01-01 05:00:03"), duration(seconds=18003)),

    ("2014-01-01", "2014-01-01 05:00:04", duration(seconds=18004)), ])
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
            duration(end=end, start=start)
        assert str(exp) == str(err.value)
    else:
        # payload
        result = duration(start=start, end=end)
        assert exp == result


# -----------------------------------------------------------------------------
@pytest.mark.parametrize("start, end, exp", [
    (1325242800, 1325246400, duration(seconds=3600)),

    (1325242801, (2011, 12, 30, 10, 0, 1), duration(seconds=-3600)),
    (1325242802, (2011, 12, 30, 10, 0),
     ValueError('need at least 6 values, no more than 9')),
    (1325242803, (2011, 12, 30, 10, 0, 0, 0, 0, 0, 0),
     ValueError('need at least 6 values, no more than 9')),

    (1325242804, time.struct_time((2011, 12, 29, 11, 0, 4, 0, 0, 0)),
     duration(days=-1)),

    (1325242805, moment('2011-12-30 11:59:59'),
     duration(minutes=59, seconds=54)),

    (1325242806, '2011-12-31', duration(hours=12, minutes=59, seconds=54)),

    # -------------------
    ((2010, 1, 1, 0, 0, 0, 0, 0, 0), 1262323937,
     duration(hours=5, minutes=32, seconds=17)),

    ((2010, 1, 1, 0, 0, 1), (2010, 1, 2, 0, 0, 0),
     duration(hours=23, minutes=59, seconds=59)),

    ((2010, 1, 1, 0, 0, 2), time.struct_time((2010, 1, 2, 0, 0, 0, 0, 0, 0)),
     duration(hours=23, minutes=59, seconds=58)),

    ((2010, 1, 1, 0, 0, 3), moment("2010-01-04 00:00:00"),
     duration(days=2, hours=23, minutes=59, seconds=57)),

    ((2010, 1, 1, 0, 0, 4), "2010-01-01 00:17:00",
     duration(minutes=16, seconds=56)),

    # -------------------
    (time.struct_time((2012, 1, 1, 0, 0, 0, 0, 0, 0)), 1325395937,
     duration(seconds=19937)),

    (time.struct_time((2012, 1, 1, 0, 0, 1, 0, 0, 0)),
     (2012, 1, 3, 0, 0, 1), duration(days=2)),

    (time.struct_time((2012, 1, 1, 0, 0, 2, 0, 0, 0)),
     time.struct_time((2012, 1, 4, 0, 0, 2, 0, 0, 0)), duration(days=3)),

    (time.struct_time((2012, 1, 1, 0, 0, 3, 0, 0, 0)),
     moment("2012-02-01 00:00:03"), duration(days=31)),

    (time.struct_time((2012, 1, 1, 0, 0, 4, 0, 0, 0)),
     "2012-01-02 07:37:42", duration(seconds=113858)),

    # -------------------
    (moment("2013-01-01"), 1357005600, duration(seconds=7200)),

    (moment("2013-01-01"), (2013, 1, 1, 2, 0, 1), duration(seconds=7201)),

    (moment("2013-01-01"), time.struct_time((2013, 1, 1, 2, 0, 2, 0, 0, 0)),
     duration(seconds=7202)),

    (moment("2013-01-01"), moment("2013-01-01 02:00:03"),
     duration(seconds=7203)),

    (moment("2013-01-01"), "2013-01-01 02:00:04", duration(seconds=7204)),

    # -------------------
    ("2014-01-01", 1388552400, duration(seconds=18000)),

    ("2014-01-01", (2014, 1, 1, 5, 0, 1), duration(seconds=18001)),

    ("2014-01-01", time.struct_time((2014, 1, 1, 5, 0, 2, 0, 0, 0)),
     duration(seconds=18002)),

    ("2014-01-01", moment("2014-01-01 05:00:03"), duration(seconds=18003)),

    ("2014-01-01", "2014-01-01 05:00:04", duration(seconds=18004)), ])
def test_dur_moment_diff(start, end, exp):
    """
    Test creating a duration by difference of moments
    """
    pytest.debug_func()
    if isinstance(exp, Exception):
        with pytest.raises(type(exp)) as err:
            # payload
            moment(end) - moment(start)
        assert str(exp) == str(err.value)
    else:
        # payload
        result = moment(end) - moment(start)
        assert exp == result


# -----------------------------------------------------------------------------
def test_dur_init_exc():
    """
    duration(start=...) and duration(end=...) should throw an exception
    """
    pytest.debug_func()
    with pytest.raises(nldt.InitError) as err:
        # payload
        duration(start=moment("2013-07-04"), years=5)
    assert "If start or end is specified, both must be" in str(err)

    with pytest.raises(nldt.InitError) as err:
        # payload
        duration(end=moment("2013-07-04"), years=5)
    assert "If start or end is specified, both must be" in str(err)


# -----------------------------------------------------------------------------
@pytest.mark.parametrize("y, w, d, h, m, s, x", [
    (0, 0, 0, 0, 0, 0, duration(seconds=0)),
    (0, 0, 0, 0, 0, 6, duration(seconds=6)),
    (0, 0, 0, 0, 5, 0, duration(seconds=300)),
    (0, 0, 0, 0, 5, 6, duration(seconds=306)),

    (0, 0, 0, 4, 0, 0, duration(seconds=4*3600)),
    (0, 0, 0, 4, 0, 6, duration(seconds=4*3600 + 6)),
    (0, 0, 0, 4, 5, 0, duration(seconds=4*3600 + 300)),
    (0, 0, 0, 4, 5, 6, duration(seconds=4*3600 + 306)),

    (0, 0, 3, 0, 0, 0, duration(seconds=3*24*3600)),
    (0, 0, 3, 0, 0, 6, duration(seconds=3*24*3600 + 6)),
    (0, 0, 3, 0, 5, 0, duration(seconds=3*24*3600 + 300)),
    (0, 0, 3, 0, 5, 6, duration(seconds=3*24*3600 + 306)),

    (0, 0, 3, 4, 0, 0, duration(seconds=76*3600)),
    (0, 0, 3, 4, 0, 6, duration(seconds=76*3600 + 6)),
    (0, 0, 3, 4, 5, 0, duration(seconds=76*3600 + 300)),
    (0, 0, 3, 4, 5, 6, duration(seconds=76*3600 + 306)),

    (0, 2, 0, 0, 0, 0, duration(seconds=14*24*3600)),
    (0, 2, 0, 0, 0, 6, duration(seconds=14*24*3600 + 6)),
    (0, 2, 0, 0, 5, 0, duration(seconds=14*24*3600 + 300)),
    (0, 2, 0, 0, 5, 6, duration(seconds=14*24*3600 + 306)),

    (0, 2, 0, 4, 0, 0, duration(seconds=340*3600)),
    (0, 2, 0, 4, 0, 6, duration(seconds=340*3600 + 6)),
    (0, 2, 0, 4, 5, 0, duration(seconds=340*3600 + 300)),
    (0, 2, 0, 4, 5, 6, duration(seconds=340*3600 + 306)),

    (0, 2, 3, 0, 0, 0, duration(seconds=408*3600)),
    (0, 2, 3, 0, 0, 6, duration(seconds=408*3600 + 6)),
    (0, 2, 3, 0, 5, 0, duration(seconds=408*3600 + 300)),
    (0, 2, 3, 0, 5, 6, duration(seconds=408*3600 + 306)),

    (0, 2, 3, 4, 0, 0, duration(seconds=412*3600)),
    (0, 2, 3, 4, 0, 6, duration(seconds=412*3600 + 6)),
    (0, 2, 3, 4, 5, 0, duration(seconds=412*3600 + 300)),
    (0, 2, 3, 4, 5, 6, duration(seconds=412*3600 + 306)),

    (1, 0, 0, 0, 0, 0, duration(seconds=31536000)),
    (1, 0, 0, 0, 0, 6, duration(seconds=31536000 + 6)),
    (1, 0, 0, 0, 5, 0, duration(seconds=31536000 + 300)),
    (1, 0, 0, 0, 5, 6, duration(seconds=31536000 + 306)),

    (1, 0, 0, 4, 0, 0, duration(seconds=8764*3600)),
    (1, 0, 0, 4, 0, 6, duration(seconds=8764*3600 + 6)),
    (1, 0, 0, 4, 5, 0, duration(seconds=8764*3600 + 300)),
    (1, 0, 0, 4, 5, 6, duration(seconds=8764*3600 + 306)),

    (1, 0, 3, 0, 0, 0, duration(seconds=368*24*3600)),
    (1, 0, 3, 0, 0, 6, duration(seconds=368*24*3600 + 6)),
    (1, 0, 3, 0, 5, 0, duration(seconds=368*24*3600 + 300)),
    (1, 0, 3, 0, 5, 6, duration(seconds=368*24*3600 + 306)),

    (1, 0, 3, 4, 0, 0, duration(seconds=8836*3600)),
    (1, 0, 3, 4, 0, 6, duration(seconds=8836*3600 + 6)),
    (1, 0, 3, 4, 5, 0, duration(seconds=8836*3600 + 300)),
    (1, 0, 3, 4, 5, 6, duration(seconds=8836*3600 + 306)),

    (1, 2, 0, 0, 0, 0, duration(seconds=379*24*3600)),
    (1, 2, 0, 0, 0, 6, duration(seconds=379*24*3600 + 6)),
    (1, 2, 0, 0, 5, 0, duration(seconds=379*24*3600 + 300)),
    (1, 2, 0, 0, 5, 6, duration(seconds=379*24*3600 + 306)),

    (1, 2, 0, 4, 0, 0, duration(seconds=9100*3600)),
    (1, 2, 0, 4, 0, 6, duration(seconds=9100*3600 + 6)),
    (1, 2, 0, 4, 5, 0, duration(seconds=9100*3600 + 300)),
    (1, 2, 0, 4, 5, 6, duration(seconds=9100*3600 + 306)),

    (1, 2, 3, 0, 0, 0, duration(seconds=9168*3600)),
    (1, 2, 3, None, None, None, duration(seconds=9168*3600)),
    (1, 2, 3, 0, 0, 6, duration(seconds=9168*3600 + 6)),
    (1, 2, 3, 0, 5, 0, duration(seconds=9168*3600 + 300)),
    (1, 2, 3, 0, 5, 6, duration(seconds=9168*3600 + 306)),

    (1, 2, 3, 4, 0, 0, duration(seconds=9172*3600)),
    (1, 2, 3, 4, 0, 6, duration(seconds=9172*3600 + 6)),
    (1, 2, 3, 4, 5, 0, duration(seconds=9172*3600 + 300)),
    (1, 2, 3, 4, 5, 6, duration(seconds=9172*3600 + 306)),
    ])
def test_dur_ywdhms(y, w, d, h, m, s, x):
    """
    Durations can initialized by any combination of years, weeks, days, hours,
    minutes, and seconds
    """
    pytest.debug_func()
    # payload
    result = duration(years=y, weeks=w, days=d, hours=h, minutes=m, seconds=s)
    assert result == x


# -----------------------------------------------------------------------------
def test_dur_add():
    """
    duration + moment-parseable => moment
    """
    pytest.debug_func()
    d = duration(hours=3)
    # payload
    assert d + "2018-01-01" == moment("2018-01-01 03:00:00")


# -----------------------------------------------------------------------------
def test_dur_sub_exc():
    """
    duration - not-num-dur-moment => exception
    """
    pytest.debug_func()
    d = duration(hours=3)
    x = [1, 2, 3]
    with pytest.raises(TypeError) as err:
        # payload
        assert d - x
    msg = ("unsupported operand type(s): '{}' and '{}'"
           .format(d.__class__, x.__class__))
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
    assert duration(years=1).dhms() == '365.00:00:00'
    assert duration(weeks=2).dhms() == '14.00:00:00'
    assert duration(days=3).dhms() == '3.00:00:00'
    assert duration(hours=4).dhms() == '0.04:00:00'
    assert duration(minutes=5).dhms() == '0.00:05:00'
    assert duration(seconds=6).dhms() == '0.00:00:06'


# -----------------------------------------------------------------------------
@pytest.mark.parametrize("dur, fmt, exp", [
    (duration(hours=2, minutes=10, seconds=24), "%H:%M:%S", "02:10:24"),
    (duration(start="2018-01-01", end="2018-01-03"), "%d.%H:%M:%S",
     "2.00:00:00"),
    (duration(seconds=93784), "%d.%H:%M:%S", "1.02:03:04"),
    (duration(seconds=26700), "%H%M", "0725"),
    (duration(start="2018-02-26", end="2018-02-25 13:00:00"), "%H%M", "-1100"),
    (duration(seconds=47277), "%d.%H:%M:%S", "0.13:07:57"),
    ])
def test_duration_format(dur, fmt, exp):
    """
    <duration>.format() -- strftime-style specifiers (where they make sense)
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
    assert dur.format(fmt) == exp


# -----------------------------------------------------------------------------
def test_duration_minus():
    """
    duration - moment should produce exception
    """
    pytest.debug_func()
    # payload (duration - duration => duration)
    assert duration(hours=1) - duration(minutes=30) == duration(seconds=1800)
    # payload (duration - number-of-seconds => duration)
    assert duration(minutes=10) - 150 == duration(seconds=450)
    with pytest.raises(TypeError) as err:
        # payload (duration - moment => exception
        assert duration(seconds=25) - moment("2018-02-01")
    assert "unsupported operand type(s): try 'moment' - 'duration'" in str(err)


# -----------------------------------------------------------------------------
def test_duration_plus():
    """
    duration + moment should produce another moment
    duration + number-of-seconds should produce another duration
    """
    pytest.debug_func()
    dur60 = duration(seconds=60)
    m1 = moment("2018-02-01 05:00:00")
    m2 = moment("2018-02-01 05:01:00")
    # payload (duration + moment => moment)
    assert dur60 + m1 == m2
    # payload (duration + duration => duration)
    assert duration(hours=1) + duration(minutes=5) == duration(seconds=3900)
    # payload (duration + number-of-seconds => duration)
    assert duration(hours=3) + 75 == duration(hours=3, minutes=1, seconds=15)


# -----------------------------------------------------------------------------
def test_duration_seconds():
    """
    duration.seconds() reports the total seconds in the duration
    """
    pytest.debug_func()
    # payload
    assert duration(years=1).seconds == 365*24*3600
    # payload
    assert duration(weeks=2).seconds == 14*24*3600
    # payload
    assert duration(days=3).seconds == 3*24*3600
    # payload
    assert duration(hours=4).seconds == 4*3600
    # payload
    assert duration(minutes=5).seconds == 300
    # payload
    assert duration(seconds=6).seconds == 6
