import pdb
import pytest
import time
import when


# -----------------------------------------------------------------------------
def test_arg_tomorrow():
    """
    Offset as an argument
    """
    then = when.when("tomorrow")
    assert then() == when.tomorrow()()


# -----------------------------------------------------------------------------
def test_arg_yesterday():
    """
    Offset as an argument
    """
    then = when.when("yesterday")
    assert then() == when.yesterday()()


# -----------------------------------------------------------------------------
def test_display():
    """
    Simply calling a when object should make it report itself in ISO format
    """
    now = time.time()
    exp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(now))
    wobj = when.when(now)
    assert wobj() == exp


# -----------------------------------------------------------------------------
def test_display_formatted():
    """
    Calling a when object with a format should make it report itself in that
    format
    """
    fmt = "%H:%M %p on %B %d, %Y"
    now = time.time()
    exp = time.strftime(fmt, time.localtime(now))
    wobj = when.when(now)
    assert wobj(fmt) == exp


# -----------------------------------------------------------------------------
def test_dst_now():
    """
    The dst function should return True or False indicating whether Daylight
    Savings Time is in force or not.
    """
    loc = time.localtime()
    if loc.tm_isdst:
        assert when.dst()
    else:
        assert not when.dst()


# -----------------------------------------------------------------------------
def test_dst_off():
    """
    The dst function should always return False for 2010-12-31
    """
    then = when.when("2010-12-31", "%Y-%m-%d")
    assert not then.dst()


# -----------------------------------------------------------------------------
def test_dst_on():
    """
    The dst function should always return True for 2012-07-01
    """
    then = when.when("2012-07-01", "%Y-%m-%d")
    assert then.dst()


# -----------------------------------------------------------------------------
def test_epoch():
    """
    Return the epoch form of times past, present, and future
    """
    now = time.time()
    yesterday = when.when(now - (24*3600))
    tomorrow = when.when(now + (24*3600))
    wobj = when.when(now)
    assert wobj.epoch() == now
    assert yesterday.epoch() == now - (24*3600)
    assert tomorrow.epoch() == now + (24*3600)


# -----------------------------------------------------------------------------
def test_with_format():
    """
    If a format is specified, the spec must match
    """
    pytest.debug_func()
    wobj = when.when('Dec 29, 2016', '%b %d, %Y')
    assert wobj() == '2016-12-29 00:00:00'
    with pytest.raises(ValueError) as err:
        wobj = when.when('Dec 29 2016', '%b %m, %Y')


# -----------------------------------------------------------------------------
@pytest.mark.parametrize("inp, exp",
                         [('Dec 29 2016', '2016-12-29 00:00:00'),
                          ('Dec 17, 1975 03:17', '1975-12-17 03:17:00'),
                          ('2000.0704 12:35:19', '2000-07-04 12:35:19'),
                          ('2000.0704 12:35', '2000-07-04 12:35:00'),
                          ('2000.0704 12', '2000-07-04 12:00:00'),
                          ('2000.0704', '2000-07-04 00:00:00'),
                          ('2007-07-04 17:17:17', '2007-07-04 17:17:17'),
                          ('2007-07-04 17:17', '2007-07-04 17:17:00'),
                          ('2007-07-04 17', '2007-07-04 17:00:00'),
                          ('2007-07-04', '2007-07-04 00:00:00'),
                          ('Jul 4 2022 19:14:10', '2022-07-04 19:14:10'),
                          ('Jul 4 2022 19:14', '2022-07-04 19:14:00'),
                          ('Jul 4 2022 19', '2022-07-04 19:00:00'),
                          ('Jul 4 2022', '2022-07-04 00:00:00'),
                          ('Jul 4, 2022 19:14:10', '2022-07-04 19:14:10'),
                          ('Jul 4, 2022 19:14', '2022-07-04 19:14:00'),
                          ('Jul 4, 2022 19', '2022-07-04 19:00:00'),
                          ('Jul 4, 2022', '2022-07-04 00:00:00'),
                          ('4 jul 2022 19:14:10', '2022-07-04 19:14:10'),
                          ('4 jul 2022 19:14', '2022-07-04 19:14:00'),
                          ('4 jul 2022 19', '2022-07-04 19:00:00'),
                          ('4 jul 2022', '2022-07-04 00:00:00'),
                          ('4 jul, 2022 19:14:10', '2022-07-04 19:14:10'),
                          ('4 jul, 2022 19:14', '2022-07-04 19:14:00'),
                          ('4 jul, 2022 19', '2022-07-04 19:00:00'),
                          ('4 jul, 2022', '2022-07-04 00:00:00'),
                          ])
def test_intuit(inp, exp):
    """
    Try to guess popular time formats
    """
    pytest.debug_func()
    later = when.when(inp)
    assert later() == exp

    
# -----------------------------------------------------------------------------
def nl_oracle(spec):
    (direction, day) = spec.split()
    if direction == 'next':
        wdidx = when.weekday_index(day)
        start = when.tomorrow()
        while int(start('%u'))-1 != wdidx:
            start = start.tomorrow()
    elif direction == 'last':
        wdidx = when.weekday_index(day)
        start = when.yesterday()
        tm = start.localtime()
        while int(start('%u'))-1 != wdidx:
            start = start.yesterday()
    elif day == 'week':
        (day, direction) = (direction, day)
        wdidx = when.weekday_index(day)
        start = when.tomorrow()
        while int(start('%u'))-1 != wdidx:
            start = start.tomorrow()
        start = start.tomorrow()
        while int(start('%u'))-1 != wdidx:
            start = start.tomorrow()
    return start()


# -----------------------------------------------------------------------------
@pytest.mark.parametrize("inp",
                         [('next monday'),
                          ('next tuesday'),
                          ('next wednesday'),
                          ('next thurssday'),
                          ('next friday'),
                          ('next saturday'),
                          ('next sunday'),
                          ('last monday'),
                          ('last tuesday'),
                          ('last wednesday'),
                          ('last thurssday'),
                          ('last friday'),
                          ('last saturday'),
                          ('last sunday'),
                          ('monday week'),
                          ('tuesday week'),
                          ('wednesday week'),
                          ('thurssday week'),
                          ('friday week'),
                          ('saturday week'),
                          ('sunday week'),
                          ])
def test_natural_language(inp):
    pytest.debug_func()
    exp = nl_oracle(inp)
    wobj = when.when(inp)
    assert wobj() == exp


# -----------------------------------------------------------------------------
def test_obj_tomorrow():
    """
    Method tomorrow() on a when object returns the date offset relative to the
    stored time.
    """
    eoy = when.when("2007-12-31")
    next = eoy.tomorrow()
    assert next() == '2008-01-01 00:00:00'


# -----------------------------------------------------------------------------
def test_obj_yesterday():
    """
    Method yesterday() on a when object returns the date offset relative to the
    stored time.
    """
    eoy = when.when("2007-12-01")
    last = eoy.yesterday()
    assert last() == '2007-11-30 00:00:00'


# -----------------------------------------------------------------------------
def test_timezone():
    """
    Timezone should return the current timezone setting
    """
    if when.dst():
        assert when.timezone() == 'EDT'
    else:
        assert when.timezone() == 'EST'


# -----------------------------------------------------------------------------
def test_tomorrow():
    """
    Method tomorrow() on a when object returns the date offset relative to the
    stored time.
    """
    tomorrow = when.tomorrow()
    now = time.time() + 24*3600
    assert abs(now - tomorrow.epoch()) < 1.0


# -----------------------------------------------------------------------------
def test_yesterday():
    """
    Method tomorrow() on a when object returns the date offset relative to the
    stored time.
    """
    yesterday = when.yesterday()
    now = time.time() - 24*3600
    assert close_times(now, yesterday.epoch())


# -----------------------------------------------------------------------------
def close_times(tm1, tm2):
    """
    Return True if the epoch times represented by *tm1* and *tm2* are 'close'
    """
    return abs(tm1 - tm2) < 0.01


# -----------------------------------------------------------------------------
# @pytest.fixture
# def nl_oracle(spec):
#     """
#     """
#     if spec == 'next saturday':
#         tm = time.localtime()
#         diff = 5 - tm.tm_wday
#         target = time.time() + diff*24*3600
#         return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(target))

