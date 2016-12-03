import pdb
import pytest
import time
import nldt


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
    Offset as an argument
    """
    meth = nldt.tomorrow()
    argl = nldt.moment('tomorrow')
    assert argl() == meth()
    obj = nldt.moment()
    obj.parse('tomorrow')
    assert obj() == meth()


# -----------------------------------------------------------------------------
def test_arg_yesterday():
    """
    Offset as an argument
    """
    then = nldt.moment("yesterday")
    assert then() == nldt.yesterday()()


# -----------------------------------------------------------------------------
def test_display():
    """
    Simply calling a nldt object should make it report itself in ISO format but
    without a time component
    """
    now = time.time()
    exp = time.strftime("%Y-%m-%d", time.localtime(now))
    wobj = nldt.moment(now)
    assert wobj() == exp


# -----------------------------------------------------------------------------
def test_display_formatted():
    """
    Calling a nldt object with a format should make it report itself in that
    format
    """
    fmt = "%H:%M %p on %B %d, %Y"
    now = time.time()
    exp = time.strftime(fmt, time.localtime(now))
    wobj = nldt.moment(now)
    assert wobj(fmt) == exp


# -----------------------------------------------------------------------------
def test_dst_now():
    """
    The dst function should return True or False indicating whether Daylight
    Savings Time is in force or not.
    """
    loc = time.localtime()
    if loc.tm_isdst:
        assert nldt.dst()
    else:
        assert not nldt.dst()


# -----------------------------------------------------------------------------
def test_dst_off():
    """
    The dst function should always return False for 2010-12-31
    """
    then = nldt.moment("2010-12-31", "%Y-%m-%d")
    assert not then.dst()


# -----------------------------------------------------------------------------
def test_dst_on():
    """
    The dst function should always return True for 2012-07-01
    """
    then = nldt.moment("2012-07-01", "%Y-%m-%d")
    assert then.dst()


# -----------------------------------------------------------------------------
def test_epoch():
    """
    Return the epoch form of times past, present, and future
    """
    now = time.time()
    yesterday = nldt.moment(now - (24*3600))
    tomorrow = nldt.moment(now + (24*3600))
    wobj = nldt.moment(now)
    assert wobj.epoch() == now
    assert yesterday.epoch() == now - (24*3600)
    assert tomorrow.epoch() == now + (24*3600)


# -----------------------------------------------------------------------------
def test_with_format():
    """
    If a format is specified, the spec must match
    """
    pytest.debug_func()
    wobj = nldt.moment('Dec 29, 2016', '%b %d, %Y')
    assert wobj() == '2016-12-29'
    with pytest.raises(ValueError) as err:
        wobj = nldt.moment('Dec 29 2016', '%b %m, %Y')


# -----------------------------------------------------------------------------
@pytest.mark.parametrize("inp, fmt, exp",
      [('Dec 29 2016', None, '2016-12-29'),
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
       ])
def test_intuit(inp, fmt, exp):
    """
    Try to guess popular time formats
    """
    pytest.debug_func()
    later = nldt.moment(inp)
    assert later(fmt) == exp

    
# -----------------------------------------------------------------------------
def nl_oracle(spec):
    """
    This function uses a simple-minded approach to find the target day. If it
    sees 'next', it counts foward to the target day. If it sees 'last', it
    counts backward, without trying to do any fancy arithmetic.
    """
    (direction, day) = spec.split()
    if spec == 'next week':
        wdidx = nldt.weekday_index('mon')
        start = nldt.tomorrow()
        while int(start('%u'))-1 != wdidx:
            start = start.tomorrow()
    elif direction == 'next':
        wdidx = nldt.weekday_index(day)
        start = nldt.tomorrow()
        while int(start('%u'))-1 != wdidx:
            start = start.tomorrow()
    elif direction == 'last':
        wdidx = nldt.weekday_index(day)
        start = nldt.yesterday()
        tm = start.localtime()
        while int(start('%u'))-1 != wdidx:
            start = start.yesterday()
    elif day == 'week':
        (day, direction) = (direction, day)
        wdidx = nldt.weekday_index(day)
        start = nldt.tomorrow()
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
                          ('next week'),
                          ('last week'),
                          ('end of the week'),
                          ('end of last week'),
                          ('beginning of next week'),
                          ('first week in January'),
                          ('week after next'),
                          ('week before last'),
                          ('a week ago'),
                          ('three weeks from now'),
                          ('two weeks ago'),
                          ('a week earlier'),
                          ('a week later'),
                          ('fourth day of this week'),
                          ('fifth day of last week'),
                          (''),
                          (''),
                          (''),
                          (''),
                          (''),
                          (''),
                          (''),
                          ])
def test_natural_language(inp):
    pytest.debug_func()
    exp = nl_oracle(inp)
    wobj = nldt.moment(inp)
    assert wobj() == exp


# -----------------------------------------------------------------------------
def test_obj_tomorrow():
    """
    Method tomorrow() on a nldt object returns the date offset relative to the
    stored time.
    """
    eoy = nldt.moment("2007-12-31")
    next = eoy.tomorrow()
    assert next() == '2008-01-01 00:00:00'


# -----------------------------------------------------------------------------
def test_obj_yesterday():
    """
    Method yesterday() on a nldt object returns the date offset relative to the
    stored time.
    """
    eoy = nldt.moment("2007-12-01")
    last = eoy.yesterday()
    assert last() == '2007-11-30 00:00:00'


# -----------------------------------------------------------------------------
def test_timezone():
    """
    Timezone should return the current timezone setting
    """
    if nldt.dst():
        assert nldt.timezone() == time.tzname[1]
    else:
        assert nldt.timezone() == time.tzname[0]


# -----------------------------------------------------------------------------
def test_tomorrow():
    """
    Method tomorrow() on a nldt object returns the date offset relative to the
    stored time.
    """
    tomorrow = nldt.tomorrow()
    now = time.time() + 24*3600
    assert abs(now - tomorrow.epoch()) < 1.0


# -----------------------------------------------------------------------------
def test_yesterday():
    """
    Method tomorrow() on a nldt object returns the date offset relative to the
    stored time.
    """
    yesterday = nldt.yesterday()
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

