import numberize
import numbers
import pydoc
import pytest
import re
import tbx
import time
import nldt
from nldt import moment as M
from calendar import timegm


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

    with pytest.raises(TypeError) as err:
        nldt.utc_offset("not a number")
    assert "utc_offset requires an epoch time or None" in str(err)


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
    This function uses a simple-minded approach to find the target day. If it
    sees 'next', it counts foward to the target day. If it sees 'last', it
    counts backward, without trying to do any fancy arithmetic.
    """
    wk = nldt.week()
    tu = nldt.time_units()
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
        start = M()
        while wk.day_number(start) != wdidx:
            start = M(start.epoch() + tu.magnitude('day'))
        return start()
    elif spec == 'last week':
        wdidx = wk.index('mon')
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
            start = M(start.epoch() + tu.magnitude('day'))
    elif direction == 'last':
        wdidx = wk.index(day)
        start = nldt.parse('yesterday')
        while wk.day_number(start) != wdidx:
            # start = M(start.epoch() - nldt._DAY)
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
        when = nldt.parse('tomorrow')
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
    exp = nl_oracle(inp)
    wobj = nldt.parse(inp)
    assert wobj() == exp


# -----------------------------------------------------------------------------
def test_ago_except():
    """
    Cover the ValueError exception in parse_ago
    """
    with pytest.raises(ValueError) as err:
        nldt.parse("no number no unit ago")
    assert "No unit found in expression" in str(err)


# -----------------------------------------------------------------------------
def test_from_now_except():
    """
    Cover the ValueError exception in parse_ago
    """
    with pytest.raises(ValueError) as err:
        nldt.parse("no number no unit from now")
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
        assert m.days(month=month, year=year) == exp
    else:
        with pytest.raises(ValueError) as err:
            m.days(month=month, year=year)
        assert exp in str(err)


# -----------------------------------------------------------------------------
def test_isleap():
    """
    When year is not given, isleap should return True if the current year is
    leap, else False
    """
    m = nldt.month()
    if m.days(2) == 29:
        assert m.isleap(None)
    else:
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

    with pytest.raises(TypeError) as err:
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
def test_moment_init_tm():
    """
    Verify instantiating a moment based on a tm tuple
    """
    foo = time.time()
    from_tm = nldt.moment(time.gmtime(foo))
    from_epoch = nldt.moment(foo)
    assert from_tm == from_epoch


# -----------------------------------------------------------------------------
def test_moment_init_except():
    """
    Verify that trying to instantiate a moment based on a tuple with too many
    or not enough elements, raises an exception
    """
    msg = "need at least 6 values, no more than 9"
    with pytest.raises(ValueError) as err:
        blah = nldt.moment((1, 2, 3, 4, 5))
    assert msg in str(err)
    with pytest.raises(ValueError) as err:
        blah = nldt.moment((1, 2, 3, 4, 5, 6, 7, 8, 9, 10))
    assert msg in str(err)


# -----------------------------------------------------------------------------
def test_moment_localtime():
    """
    Test moment().localtime()
    """
    now = time.time()
    foo = nldt.moment(now)
    expected = time.localtime(now)
    actual = foo.localtime()
    assert actual == expected


# -----------------------------------------------------------------------------
def test_moment_ceiling():
    """
    Test in moment().ceiling()
    """

    def expected_ceiling(unit, now):
        if unit in ['second', 'minute', 'hour', 'day']:
            mag = tu.magnitude(unit)
            exp = now + mag - (now % mag) - 1
        elif unit == 'week':
            tm = time.gmtime(now)
            delta = wk.forediff(tm.tm_wday, 'mon')
            nflr = timegm((tm.tm_year, tm.tm_mon, tm.tm_mday + delta,
                           0, 0, 0, 0, 0, 0))
            exp = nflr - 1
        elif unit == 'month':
            tm = time.gmtime(now)
            nflr = timegm((tm.tm_year, tm.tm_mon+1, 1, 0, 0, 0, 0, 0, 0))
            exp = nflr - 1
        elif unit == 'year':
            tm = time.gmtime(now)
            nflr = timegm((tm.tm_year+1, 1, 1, 0, 0, 0, 0, 0, 0))
            exp = nflr - 1
        return nldt.moment(exp)

    tu = nldt.time_units()
    wk = nldt.week()
    now = time.time()
    mug = nldt.moment(now)
    for unit in tu.unit_list():
        assert mug.ceiling(unit) == expected_ceiling(unit, now)

    with pytest.raises(ValueError) as err:
        mug.ceiling('frumpy')
    assert "'frumpy' is not a time unit" in str(err)


# -----------------------------------------------------------------------------
def test_moment_floor():
    """
    Test in moment().floor()
    """

    def expected_floor(unit, now):
        if unit in ['second', 'minute', 'hour', 'day']:
            mag = tu.magnitude(unit)
            exp = now - (now % mag)
        elif unit == 'week':
            tm = time.gmtime(now)
            delta = wk.backdiff(tm.tm_wday, 'mon')
            exp = timegm((tm.tm_year, tm.tm_mon, tm.tm_mday - delta,
                          0, 0, 0, 0, 0, 0))
        elif unit == 'month':
            tm = time.gmtime(now)
            exp = timegm((tm.tm_year, tm.tm_mon, 1, 0, 0, 0, 0, 0, 0))
        elif unit == 'year':
            tm = time.gmtime(now)
            exp = timegm((tm.tm_year, 1, 1, 0, 0, 0, 0, 0, 0))
        return nldt.moment(exp)

    pytest.debug_func()
    tu = nldt.time_units()
    wk = nldt.week()
    now = time.time()
    mug = nldt.moment(now)
    for unit in tu.unit_list():
        assert mug.floor(unit) == expected_floor(unit, now)

    with pytest.raises(ValueError) as err:
        mug.floor('frumpy')
    assert "'frumpy' is not a time unit" in str(err)
