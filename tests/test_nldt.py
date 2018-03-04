"""
nldt - Natural Language Date/Time support
Copyright (c) 2017 - <the end of time>  Tom Barron
See file LICENSING for details

This file contains code for testing nldt functionality.
"""
from fixtures import fx_calls_debug    # noqa
from tzlocal import get_localzone
from datetime import datetime
from nldt import numberize
import numbers
import os
import pytest
import re
import time
import nldt
from nldt import moment as M

nldt.moment.default_tz('clear')


# -----------------------------------------------------------------------------
def test_bug_pctsec():
    """
    given
        x = moment()
    x.epoch() should be equal to int(x('%s'))
    """
    pytest.debug_func()
    now = nldt.moment()
    assert now.epoch() == int(now("%s"))


# -----------------------------------------------------------------------------
def test_clock():
    """
    nldt.clock() is an alias for time.clock()
    """
    pytest.debug_func()
    assert abs(nldt.clock() - time.clock()) < 0.0001


# -----------------------------------------------------------------------------
def test_tz_context_keyerr():
    """
    Test for 'with nldt.tz_context(ZONE)' when 'TZ' is not in os.environ (so
    pre-fix, 'del os.environ['TZ']' throws a KeyError)
    """
    pytest.debug_func()
    tzorig = None
    if 'TZ' in os.environ:
        tzorig = os.getenv('TZ')

    with nldt.tz_context('US/Pacific'):
        then = M("2000-12-31 15:59:59", itz='US/Pacific')
        assert then("%F %T") == "2000-12-31 15:59:59"

    if tzorig:
        os.environ['TZ'] = tzorig
    elif 'TZ' in os.environ:
        del os.environ['TZ']


# -----------------------------------------------------------------------------
@pytest.mark.parametrize("zname, std, soff, dst, doff", [
    pytest.param('US/Eastern', 'EST', 18000, 'EDT', 14400, id='001'),
    pytest.param('US/Central', 'CST', 21600, 'CDT', 18000, id='002'),
    pytest.param('US/Mountain', 'MST', 25200, 'MDT', 21600, id='003'),
    pytest.param('US/Pacific', 'PST', 28800, 'PDT', 25200, id='004'),
    pytest.param('Asia/Jakarta', 'WIB', -25200, 'WIB', -25200, id='005'),
    ])
def test_tz_context_explicit(zname, std, soff, dst, doff):
    """
    Verify that 'with nldt.tz_context(FOOBAR)' creates a context with FOOBAR as
    the local timezone.
    """
    pytest.debug_func()
    with nldt.tz_context(zname):
        assert time.timezone == soff
        assert time.altzone == doff
        assert time.daylight == (soff != doff)
        assert time.tzname == (std, dst)


# -----------------------------------------------------------------------------
# @pytest.mark.parametrize("zname", pytz.all_timezones)
# def test_tz_context(zname):
#     """
#     Verify that 'with tz_context()' does the right thing for all timezones
#     """
#     pytest.debug_func()
#     zone = pytz.timezone(zname)
#     # now = datetime.now()
#     # for idx, point in enumerate(zone._utc_transition_times):
#     #     if now < point:
#     #         when_idx = idx
#     #         break
#     # dt_std = zone._utc_transition_times[-1]
#     exp_std = -1 * zone.utcoffset(datetime(2011, 1, 1)).total_seconds()
#     exp_dst = -1 * zone.utcoffset(datetime(2011, 7, 1)).total_seconds()
#     with nldt.tz_context(zname):
#         assert time.timezone == exp_std
#         assert time.altzone == exp_dst
#         assert time.daylight == (exp_std != exp_dst)


# -----------------------------------------------------------------------------
def test_tz_context_default():
    """
    Test default timezone context
    """
    pytest.debug_func()
    lz = get_localzone()
    std_dt = datetime(2011, 1, 1)
    std_offset = lz.utcoffset(std_dt).total_seconds()
    std_name = lz.tzname(std_dt)
    dst_dt = datetime(2011, 7, 1)
    dst_offset = lz.utcoffset(dst_dt).total_seconds()
    dst_name = lz.tzname(dst_dt)
    with nldt.tz_context():
        assert time.timezone == -1 * std_offset
        assert time.altzone == -1 * dst_offset
        assert time.daylight == (std_offset != dst_offset)
        assert time.tzname == (std_name, dst_name)


# -----------------------------------------------------------------------------
def test_tz_context_nested():
    """
    Test nested timezone contexts
    """
    pytest.debug_func()
    with nldt.tz_context('Pacific/Honolulu'):
        assert time.timezone == 36000
        assert time.altzone == 36000
        assert time.daylight == 0
        assert time.tzname == ('HST', 'HST')
        with nldt.tz_context('US/Mountain'):
            assert time.timezone == 25200
            assert time.altzone == 21600
            assert time.daylight == 1
            assert time.tzname == ('MST', 'MDT')


# -----------------------------------------------------------------------------
def test_indexable_abc():
    """
    Indexable is an abstract base class that should not be instantiated
    directly.
    """
    pytest.debug_func()
    msg = "This is an abstract base class -- don't instantiate it."
    with pytest.raises(TypeError) as err:
        _ = nldt.Indexable()
        assert isinstance(_, nldt.Indexable)
    assert msg in str(err)


# -----------------------------------------------------------------------------
@pytest.mark.parametrize("zname, std, soff, dst, doff", [
    pytest.param('US/Eastern', 'EST', 18000, 'EDT', 14400, id='001'),
    pytest.param('US/Central', 'CST', 21600, 'CDT', 18000, id='002'),
    pytest.param('US/Mountain', 'MST', 25200, 'MDT', 21600, id='003'),
    pytest.param('US/Pacific', 'PST', 28800, 'PDT', 25200, id='004'),
    ])
def test_local(zname, std, soff, dst, doff):
    """
    nldt.local.timezone() should return the same value as time.timezone() for
    the currently configured local timezone
    """
    pytest.debug_func()
    seed = "{}{}{}{}".format(std, int(soff/3600), dst, int(doff/3600))
    os.environ['TZ'] = seed
    time.tzset()
    lz = nldt.local()
    assert time.timezone == lz.timezone()
    assert time.altzone == lz.altzone()
    assert time.daylight == lz.daylight()
    assert time.tzname == lz.tzname()


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
    pytest.debug_func()
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
    pytest.debug_func()
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
    pytest.debug_func()
    w = nldt.week()
    result = w.day_list()
    exp = ['monday', 'tuesday', 'wednesday', 'thursday',
           'friday', 'saturday', 'sunday']
    assert result == exp


# -----------------------------------------------------------------------------
def test_utc_offset():
    """
    Check routine utc_offset() against some known timezones that don't change
    with dst
    """
    pytest.debug_func()
    m_dst_off = M("2001-01-01")
    m_dst_on = M("2001-07-01")
    assert nldt.utc_offset(tz='Singapore') == 8 * 3600

    assert nldt.utc_offset(m_dst_off.epoch(), tz='Pacific/Apia') == -11 * 3600
    assert nldt.utc_offset(m_dst_on.epoch(), tz='Pacific/Apia') == -11 * 3600

    # The expected value must be computed based on the local timezone, not
    # assumed to be Eastern.
    loc = get_localzone()
    exp_off = loc.utcoffset(datetime.fromtimestamp(m_dst_off.epoch()))
    exp_on = loc.utcoffset(datetime.fromtimestamp(m_dst_on.epoch()))
    assert nldt.utc_offset(m_dst_off.epoch()) == exp_off.total_seconds()
    assert nldt.utc_offset(m_dst_on.epoch()) == exp_on.total_seconds()

    # Note: we have to multiply time.{alt,time}zone by -1 here because the time
    # module, based on the Unix standard, assumes zones east of UTC have a
    # negative offset while those west of UTC have a positive offset. The UTC
    # standard defines this in the opposite way, assigning positive offsets to
    # the east and negative offsets to the west.
    #
    # With the UTC standard,
    #
    #      localtime = UTC + offset
    #      UTC = localtime - offset
    #
    # With the Unix standard,
    #
    #      localtime = UTC - offset
    #      UTC = localtime + offset
    #
    tm = time.localtime()
    if tm.tm_isdst:
        assert nldt.utc_offset() == -1 * time.altzone
    else:
        assert nldt.utc_offset() == -1 * time.timezone

    with pytest.raises(TypeError) as err:
        nldt.utc_offset("not a number")
    assert "utc_offset requires an epoch time or None" in str(err)


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
    assert nldt.dst(then.epoch(), tz="US/Eastern")


# -----------------------------------------------------------------------------
def test_dst_elsewhere_off():
    """
    The dst function should return False for non local timezones that support
    DST during times of the year when DST is not in force.

    NOTE: It seems that DST flags are reversed in the southern hemisphere (just
    like the seasons, duh), so we expect New Zealand's flag to be off when most
    others are on.

    NOTE: The pytz table indicates that the last transition time for the
    Africa/Addis_Ababa timezone was in 1959 and that the last time segment has
    a dst offset of 0, so we're using that as an example of DST being
    permanently off.
    """
    pytest.debug_func()
    then = nldt.moment("2012-01-01")
    assert not nldt.dst(then.epoch(), "US/Alaska")
    assert not nldt.dst(then.epoch(), "Africa/Addis_Ababa")
    assert nldt.dst(then.epoch(), "NZ")


# -----------------------------------------------------------------------------
def test_dst_list():
    """
    If function dst() gets an argument that is not str, number, or moment it
    throws an exception
    """
    pytest.debug_func()
    with pytest.raises(TypeError) as err:
        nldt.dst(time.gmtime())
    assert "dst() when arg must be str, number, or moment" in str(err)


# -----------------------------------------------------------------------------
def test_dst_elsewhere_on():
    """
    The dst function should return True for non local timezones that support
    DST during times of the year when DST IS in force.
    """
    pytest.debug_func()
    then = nldt.moment("2012-07-01")
    assert nldt.dst(then.epoch(), "US/Alaska")
    assert not nldt.dst(then.epoch(), "NZ")


# -----------------------------------------------------------------------------
def test_dst_utc():
    """
    For UTC, dst should always be off
    """
    pytest.debug_func()
    now = nldt.moment()
    curyear = int(now("%Y"))
    for year in range(curyear-5, curyear+6):
        for pitstr in ["{}-01-01".format(year), "{}-07-01".format(year)]:
            pit = nldt.moment(pitstr)
            assert not nldt.dst(pit.epoch(), "UTC")


# -----------------------------------------------------------------------------
def test_parse_unbound_local():
    """
    An unparseable input is causing a traceback
    """
    pytest.debug_func()
    prs = nldt.Parser()
    with pytest.raises(nldt.ParseError) as err:
        prs("one two")
    msg = "Failure parsing 'one two' -- not recognized as a time expression"
    assert msg in str(err)
    assert "UnboundLocalError" not in str(err)


# -----------------------------------------------------------------------------
def test_parse_now():
    """
    Test for nldt.Parser() object parsing 'now'
    """
    pytest.debug_func()
    prs = nldt.Parser()
    q = M()
    then = M(time.time() - 30)
    assert prs('now') == q
    assert prs('now', q) == q
    assert prs('now', then) == then


# -----------------------------------------------------------------------------
def test_parse_tomorrow():
    """
    Calling parse with 'tomorrow' and a moment object should return a moment
    set to the following day.
    """
    pytest.debug_func()
    eoy = nldt.moment("2007-12-31")
    assert not hasattr(eoy, 'parse')
    prs = nldt.Parser()
    result = prs('tomorrow', start=eoy)
    assert result() == '2008-01-01'
    feb28 = nldt.moment("2012-02-28")
    result = prs('tomorrow', start=feb28)
    assert result() == '2012-02-29'


# -----------------------------------------------------------------------------
def test_parse_yesterday():
    """
    Parsing 'yesterday' relative to a moment goes bacward on the calendar
    """
    pytest.debug_func()
    eoy = nldt.moment("2007-12-01")
    assert not hasattr(eoy, 'parse')
    prs = nldt.Parser()
    result = prs('yesterday', start=eoy)
    assert result() == '2007-11-30'
    mar1 = nldt.moment("2008-03-01")
    result = prs('yesterday', start=mar1)
    assert result() == "2008-02-29"


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
    This function provides an oracle for tests of nldt.Parser. In this
    function, we use a simple-minded approach to find the target day. If we see
    'next', we count foward to the target day. If we see 'last', we count
    backward, without trying to do any fancy arithmetic.
    """
    wk = nldt.week()
    tu = nldt.time_units()
    prs = nldt.Parser()
    if spec == 'fourth day of this week':
        now = prs('last week')
        now = prs('next week', now)
        now = prs('next thursday', now)
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
        start = prs('tomorrow')
        while wk.day_number(start) != wdidx:
            start = M(start.epoch() + tu.magnitude('day'))
        return start()
    elif spec == 'last week':
        wdidx = wk.index('mon')
        start = prs('yesterday')
        start = nldt.moment(start.epoch() - 6*24*3600)
        while wk.day_number(start) != wdidx:
            start = prs('yesterday', start)
        return start()
    elif spec == 'end of the week':
        wdidx = 6
        start = nldt.moment()
        while wk.day_number(start) != wdidx:
            start = prs('tomorrow', start)
        return start()
    elif spec == 'end of last week':
        eolw = M(nldt.moment().week_floor().epoch() - 1)
        return eolw()
    elif spec == 'beginning of next week':
        wdidx = 0
        start = prs('tomorrow')
        while wk.day_number(start) != wdidx:
            start = prs('tomorrow', start)
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
        nxwk = prs('next week')
        nxwk = prs('next week', nxwk)
        return nxwk(otz='utc')
    elif spec == 'week before last':
        lswk = prs('last week')
        lswk = prs('last week', lswk)
        return lswk(otz='utc')
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
                start = prs('yesterday', start)
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
        start = prs('tomorrow')
        while start.localtime().tm_wday != wdidx:
            start = M(start.epoch() + tu.magnitude('day'))
    elif direction == 'last':
        wdidx = wk.index(day)
        start = prs('yesterday')
        while start.localtime().tm_wday != wdidx:
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
        when = prs('tomorrow')
        while wk.day_number(when) != wdidx:
            when = M(when.epoch() + tu.magnitude('day'))

        # now jump forward a week
        start = M(when.epoch() + tu.magnitude('week'))

    return start()


# -----------------------------------------------------------------------------
@pytest.mark.parametrize("inp", [
    pytest.param('last week', id='001'),
    pytest.param('next year', id='002'),
    pytest.param('next monday', id='003'),
    pytest.param('next tuesday', id='004'),
    pytest.param('next wednesday', id='005'),
    pytest.param('next thursday', id='006'),
    pytest.param('next friday', id='007'),
    pytest.param('next saturday', id='008'),
    pytest.param('next sunday', id='009'),
    pytest.param('next week', id='010'),
    pytest.param('next month', id='011'),
    pytest.param('last monday', id='012'),
    pytest.param('last tuesday', id='013'),
    pytest.param('last wednesday', id='014'),
    pytest.param('last thursday', id='015'),
    pytest.param('last friday', id='016'),
    pytest.param('last saturday', id='017'),
    pytest.param('last sunday', id='018'),
    pytest.param('last month', id='019'),
    pytest.param('last year', id='020'),
    pytest.param('today', id='021'),
    pytest.param('tomorrow', id='022'),
    pytest.param('yesterday', id='023'),
    pytest.param('monday week', id='024'),
    pytest.param('tuesday week', id='025'),
    pytest.param('wednesday week', id='026'),
    pytest.param('thursday week', id='027'),
    pytest.param('friday week', id='028'),
    pytest.param('saturday week', id='029'),
    pytest.param('sunday week', id='030'),
    pytest.param('end of last week', id='031'),
    pytest.param('end of the week', id='032'),
    pytest.param('beginning of next week', id='033'),
    pytest.param('first week in January', id='034'),
    pytest.param('first week in June', id='035'),
    pytest.param('week after next', id='036'),
    pytest.param('week before last', id='037'),
    pytest.param('a week ago', id='038'),
    pytest.param('three weeks from now', id='039'),
    pytest.param('two weeks ago', id='040'),
    pytest.param('a week earlier', id='041'),
    pytest.param('a week later', id='042'),
    # pytest.param('fourth day of this week', id='043'),
    # pytest.param('fifth day of last week', id='044'),
    # pytest.param('beginning of this week', id='045'),
    ])
def test_natural_language(inp):
    pytest.debug_func()
    prs = nldt.Parser()
    exp = nl_oracle(inp)
    wobj = prs(inp)
    assert wobj(otz='utc') == exp


# -----------------------------------------------------------------------------
def test_ago_except():
    """
    Cover the ValueError exception in parse_ago
    """
    pytest.debug_func()
    prs = nldt.Parser()
    with pytest.raises(ValueError) as err:
        prs("no number no unit ago")
    assert "No unit found in expression" in str(err)


# -----------------------------------------------------------------------------
def test_from_now_except():
    """
    Cover the ValueError exception in parse_ago
    """
    pytest.debug_func()
    prs = nldt.Parser()
    with pytest.raises(ValueError) as err:
        prs("no number no unit from now")
    assert "No unit found in expression" in str(err)


# -----------------------------------------------------------------------------
@pytest.mark.parametrize("month, year, exp", [
    pytest.param(1, None, 31, id='001'),
    pytest.param(2, 2017, 28, id='002'),
    pytest.param(2, 2016, 29, id='003'),
    pytest.param(2, 2000, 29, id='004'),
    pytest.param(2, 1900, 28, id='005'),
    pytest.param(3, 2018, 31, id='006'),
    pytest.param(4, None, 30, id='007'),

    pytest.param(5, None, 31, id='008'),
    pytest.param(6, None, 30, id='009'),
    pytest.param(7, None, 31, id='010'),
    pytest.param(8, None, 31, id='011'),
    pytest.param(9, None, 30, id='012'),
    pytest.param(10, None, 31, id='013'),
    pytest.param(11, None, 30, id='014'),
    pytest.param(12, None, 31, id='015'),
    pytest.param(19, None, "Could not indexify", id='016'),
    ])
def test_month_days(month, year, exp):
    """
    Get the number of days in each month
    """
    pytest.debug_func()
    m = nldt.month()
    if isinstance(exp, numbers.Number):
        # payload
        assert m.days(month=month, year=year) == exp
    else:
        with pytest.raises(ValueError) as err:
            # payload
            m.days(month=month, year=year)
        assert exp in str(err)


# -----------------------------------------------------------------------------
def test_month_days_curyear():
    """
    Verify that month.days() for february this year does the right thing
    """
    pytest.debug_func()
    mobj = nldt.month()
    now = nldt.moment()
    curyear = int(now('%Y'))
    exp = 29 if mobj.isleap(curyear) else 28
    # payload
    assert mobj.days(2) == exp


# -----------------------------------------------------------------------------
def test_isleap():
    """
    When year is not given, isleap should return True if the current year is
    leap, else False
    """
    pytest.debug_func()
    m = nldt.month()
    if m.days(2) == 29:
        # payload
        assert m.isleap(None)
    else:
        # payload
        assert not m.isleap(None)


# -----------------------------------------------------------------------------
def test_match_monthnames():
    """
    Verify the regex returned by month.match_monthnames
    """
    pytest.debug_func()
    m = nldt.month()
    exp = "|".join(m.names())
    exp = "(" + exp + ")"
    assert exp == m.match_monthnames()


# -----------------------------------------------------------------------------
@pytest.mark.parametrize("inp, exp", [
    pytest.param("No weekday name in this text", None, id='001'),
    pytest.param("Can you find the wednesday?", "wednesday", id='002'),
    pytest.param("Here it is monday again", "monday", id='003'),
    pytest.param("tuesday is a fine day", "tuesday", id='004'),
    pytest.param("...Saturday we'll go to the store", 'saturday', id='005'),
    pytest.param("Which day precedes (Friday) and which follows?", 'friday',
                 id='006'),
    pytest.param("Still need a Thursday test", 'thursday', id='007'),
    pytest.param("On Sunday all the tests are finished", 'sunday', id='008'),
    ])
def test_find_day(inp, exp):
    """
    Coverage for week.find_day
    """
    pytest.debug_func()
    w = nldt.week()
    assert w.find_day(inp) == exp


# -----------------------------------------------------------------------------
@pytest.mark.parametrize("inp, exp", [
    pytest.param(0, "monday", id='001'),
    pytest.param("0", "monday", id='002'),
    pytest.param("mon", "monday", id='003'),

    pytest.param(1, "tuesday", id='004'),
    pytest.param("1", "tuesday", id='005'),
    pytest.param("tue", "tuesday", id='006'),

    pytest.param(2, "wednesday", id='007'),
    pytest.param("2", "wednesday", id='008'),
    pytest.param("wed", "wednesday", id='009'),

    pytest.param(3, "thursday", id='010'),
    pytest.param("3", "thursday", id='011'),
    pytest.param("thu", "thursday", id='012'),

    pytest.param(4, "friday", id='013'),
    pytest.param("4", "friday", id='014'),
    pytest.param("fri", "friday", id='015'),

    pytest.param(5, "saturday", id='016'),
    pytest.param("5", "saturday", id='017'),
    pytest.param("sat", "saturday", id='018'),

    pytest.param(6, "sunday", id='019'),
    pytest.param("6", "sunday", id='020'),
    pytest.param("sun", "sunday", id='021'),

    pytest.param(13, "except", id='022'),
    pytest.param("13", "except", id='023'),
    pytest.param("nosuch", "except", id='024'),
    ])
def test_week_fullname(inp, exp):
    """
    Test week.fullname
    """
    pytest.debug_func()
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
    pytest.debug_func()
    w = nldt.week()
    sat = nldt.moment("2000-01-01")
    sun = nldt.moment("2000-01-02")

    assert w.day_number(sat.epoch()) == 5
    assert w.day_number(sat) == 5

    with pytest.raises(TypeError) as err:
        # payload
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
def test_unit_list():
    """
    Verify time_units().unit_list()
    """
    pytest.debug_func()
    tu = nldt.time_units()
    exp = ["second", "minute", "hour", "day", "week", "month", "year"]
    assert list(tu.unit_list()) == exp


# -----------------------------------------------------------------------------
def test_parser_research():
    """
    Parser research method throws an exception if its third argument is not a
    list
    """
    pytest.debug_func()
    prs = nldt.Parser()
    frink = "this is a string"
    with pytest.raises(TypeError) as err:
        if prs.research("boofar", "one two boofar three four", frink):
            assert frink == "this is a string"
    assert "result must be an empty list" in str(err)


# -----------------------------------------------------------------------------
def test_Stub():
    """
    The Stub class raises an exception reporting the current function that
    needs attention
    """
    pytest.debug_func()
    with pytest.raises(nldt.Stub) as err:
        raise nldt.Stub("extra text")
    msg = "test_Stub() is a stub -- please complete it. (extra text)"
    assert msg in str(err)


# -----------------------------------------------------------------------------
def test_caller_name():
    """
    Test function caller_name()
    """
    pytest.debug_func()

    def foobar():
        assert nldt.caller_name() == 'test_caller_name'

    foobar()
