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


