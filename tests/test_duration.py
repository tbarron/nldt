import nldt
from nldt import moment as M
from nldt import duration as D
import pytest
import time


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
    Test creating a duration by difference of times in various formats (epoch,
    tuple, time.struct_time, ISO-inited moment, and bare ISO format time
    string)
    """
    pytest.debug_func()
    if isinstance(exp, Exception):
        with pytest.raises(type(exp)) as err:
            # payload
            _ = D(end=end, start=start)
        assert str(exp) == str(err.value)
    else:
        # payload
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
    Test creating a duration by difference of moments
    """
    pytest.debug_func()
    if isinstance(exp, Exception):
        with pytest.raises(type(exp)) as err:
            # payload
            _ = M(end) - M(start)
        assert str(exp) == str(err.value)
    else:
        # payload
        result = M(end) - M(start)
        assert exp == result


# -----------------------------------------------------------------------------
def test_dur_init_exc():
    """
    D(start=...) and D(end=...) should throw an exception
    """
    pytest.debug_func()
    with pytest.raises(nldt.InitError) as err:
        # payload
        _ = D(start=M("2013-07-04"), years=5)
    assert "If start or end is specified, both must be" in str(err)

    with pytest.raises(nldt.InitError) as err:
        # payload
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
    # payload
    assert D(years=y, weeks=w, days=d, hours=h, minutes=m, seconds=s) == x


# -----------------------------------------------------------------------------
def test_dur_add():
    """
    duration + moment-parseable => moment
    """
    d = D(hours=3)
    # payload
    assert d + "2018-01-01" == M("2018-01-01 03:00:00")
    msg = ("unsupported operand type(s) for +: "
           "'<class 'nldt.moment'>' and '<class 'list'>'")


# -----------------------------------------------------------------------------
def test_dur_sub_exc():
    """
    duration - not-num-dur-moment => exception
    """
    pytest.debug_func()
    d = D(hours=3)
    x = [1,2,3]
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
    assert D(years=1).dhms() == '365.00:00:00'
    assert D(weeks=2).dhms() == '14.00:00:00'
    assert D(days=3).dhms() == '3.00:00:00'
    assert D(hours=4).dhms() == '0.04:00:00'
    assert D(minutes=5).dhms() == '0.00:05:00'
    assert D(seconds=6).dhms() == '0.00:00:06'


# -----------------------------------------------------------------------------
@pytest.mark.parametrize("dur, fmt, exp", [
    (D(hours=2, minutes=10, seconds=24), "%H:%M:%S", "02:10:24"),
    (D(start="2018-01-01", end="2018-01-03"), "%d.%H:%M:%S", "2.00:00:00"),
    (D(seconds=93784), "%d.%H:%M:%S", "1.02:03:04"),
    (D(seconds=26700), "%H%M", "0725"),
    (D(start="2018-02-26", end="2018-02-25 13:00:00"), "%H%M", "-1100"),
    (D(seconds=47277), "%d.%H:%M:%S", "0.13:07:57"),
    ])
def test_duration_format(dur, fmt, exp):
    """
    duration.format() -- strftime-style specifiers (where they make sense)
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
    assert dur.format(fmt) == exp


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
def test_duration_seconds():
    """
    duration.seconds() reports the total seconds in the duration
    """
    assert D(years=1).seconds == 365*24*3600
    assert D(weeks=2).seconds == 14*24*3600
    assert D(days=3).seconds == 3*24*3600
    assert D(hours=4).seconds == 4*3600
    assert D(minutes=5).seconds == 300
    assert D(seconds=6).seconds == 6
