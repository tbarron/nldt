import numberize
import numbers
import pydoc
import pytest
import re
import tbx
import time
import nldt
from nldt import moment as M

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
    assert nldt.month_index('jan') == 1
    assert nldt.month_index('February') == 2
    assert nldt.month_index('marc') == 3
    assert nldt.month_index('apr') == 4
    assert nldt.month_index('May') == 5
    assert nldt.month_index('june') == 6
    assert nldt.month_index('jul') == 7
    assert nldt.month_index('August') == 8
    assert nldt.month_index('sep') == 9
    assert nldt.month_index('Octob') == 10
    assert nldt.month_index('nov') == 11
    assert nldt.month_index('December') == 12
    with pytest.raises(KeyError):
        assert nldt.month_index('frobble')


# -----------------------------------------------------------------------------
def test_month_names():
    """
    nldt.month_names() returns the list of month names in order
    """
    result = nldt.month_names()
    exp = ['january', 'february', 'march', 'april', 'may', 'june',
           'july', 'august', 'september', 'october', 'november', 'december']
    assert result == exp


# -----------------------------------------------------------------------------
def test_weekday_index():
    """
    nldt.weekday_index() takes a weekday name and returns its index. On bad
    input, it will raise a KeyError.
    """
    assert nldt.weekday_index('Monday') == 0
    assert nldt.weekday_index('tue') == 1
    assert nldt.weekday_index('wednesday') == 2
    assert nldt.weekday_index('thur') == 3
    assert nldt.weekday_index('fri') == 4
    assert nldt.weekday_index('Saturday') == 5
    assert nldt.weekday_index('sunda') == 6
    with pytest.raises(KeyError):
        assert nldt.weekday_index('foobar')


# -----------------------------------------------------------------------------
def test_weekday_names():
    """
    nldt.weekday_names() returns the list of weekday names in order
    """
    result = nldt.weekday_names()
    exp = ['monday', 'tuesday', 'wednesday', 'thursday',
           'friday', 'saturday', 'sunday']
    assert result == exp


# -----------------------------------------------------------------------------
# def test_obj_timezone_dstoff():
#     """
#     Querying the timezone on an object whose moment is set outside DST will get
#     a timezone name reflecting standard time
#     """
#     obj = nldt.moment('2016.1201')
#     assert obj.timezone() == time.tzname[0]


# -----------------------------------------------------------------------------
# def test_obj_timezone_dston():
#     """
#     Querying the timezone on an object whose moment is set during DST will get
#     a timezone name reflecting DST
#     """
#     obj = nldt.moment('2016.0701')
#     assert obj.timezone() == time.tzname[1]


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
    Offset as an argument. moment('tomorrow') generates the beginning of
    tomorrow.
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
def test_parse_tomorrow():
    """
    Calling parse with 'tomorrow' and a moment object should return a moment
    set to the following day.
    """
    pytest.debug_func()
    eoy = nldt.moment("2007-12-31")
    assert not hasattr(eoy, 'parse')
    result = nldt.parse('tomorrow', start=eoy)
    assert result() == '2008-01-01'


# -----------------------------------------------------------------------------
def test_parse_yesterday():
    """
    Asking an object to parse 'yesterday' moves it bacward on the calendar
    """
    pytest.debug_func()
    eoy = nldt.moment("2007-12-01")
    assert not hasattr(eoy, 'parse')
    result = nldt.parse('yesterday', start=eoy)
    assert result() == '2007-11-30'


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
# def word_before(text, selector):
#     """
#     return the word preceding *selector* in *text*
#     """
#     words = text.split()
#     next = False
#     rval = None
#     for w in reversed(words):
#         if next:
#             rval = w
#             break
#         elif w == selector:
#             next = True
#     return rval


# -----------------------------------------------------------------------------
def nl_oracle(spec):
    """
    This function uses a simple-minded approach to find the target day. If it
    sees 'next', it counts foward to the target day. If it sees 'last', it
    counts backward, without trying to do any fancy arithmetic.
    """
    wk = nldt.week()
    if spec == 'fourth day of this week':
        now = nldt.parse('last week')
        now = nldt.parse('next week', now)
        now = nldt.parse('next thursday', now)
        return now()
    elif spec == 'fifth day of last week':
        now = nldt.moment('last week')
        now.parse('next friday')
        return now()
    elif spec == 'today':
        return time.strftime("%Y-%m-%d")
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
        start = M()
        while wk.day_number(start) != wdidx:
            start = M(start.epoch() + nldt._DAY)
        return start()
    elif spec == 'last week':
        wdidx = nldt.weekday_index('mon')
        start = nldt.parse('yesterday')
        start = nldt.moment(start.epoch() - 6*24*3600)
        while wk.day_number(start) != wdidx:
            start = nldt.parse('yesterday', start)
        return start()
    elif spec == 'end of the week':
        wdidx = 6
        start = nldt.moment()
        while wk.day_number(start) != wdidx:
            start = nldt.parse('tomorrow', start)
        return start()
    elif spec == 'end of last week':
        eolw = M(nldt.moment().week_floor().epoch() - 1)
        return eolw()
    elif spec == 'beginning of next week':
        wdidx = 0
        start = nldt.parse('tomorrow')
        while wk.day_number(start) != wdidx:
            start = nldt.parse('tomorrow', start)
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
        nxwk = nldt.parse('next week')
        nxwk = nldt.parse('next week', nxwk)
        return nxwk()
    elif spec == 'week before last':
        lswk = nldt.parse('last week')
        lswk = nldt.parse('last week', lswk)
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
                start = nldt.parse('yesterday', start)
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
        start = nldt.parse('tomorrow')
        while wk.day_number(start) != wdidx:
            start = M(start.epoch() + nldt._DAY)
    elif direction == 'last':
        wdidx = wk.index(day)
        start = nldt.parse('yesterday')
        while wk.day_number(start) != wdidx:
            start = M(start.epoch() - nldt._DAY)
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
        when = nldt.parse('tomorrow')
        while wk.day_number(when) != wdidx:
            when = M(when.epoch() + nldt._DAY)

        # now jump forward a week
        start = M(when.epoch() + nldt._WEEK)

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
    exp = nl_oracle(inp)
    wobj = nldt.parse(inp)
    assert wobj() == exp


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
