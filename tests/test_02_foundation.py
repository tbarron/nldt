"""
nldt - Natural Language Date/Time support
Copyright (c) 2017 - <the end of time>  Tom Barron
See file LICENSING for details

This file contains code for testing nldt functionality.
"""
from datetime import datetime
from tzlocal import get_localzone
from nldt import moment as M
import nldt
import numbers
import pytest
import pytz
import re
import time
from nldt.text import txt
import text_extend                               # noqa


# -----------------------------------------------------------------------------
def test_clock():
    """
    nldt.clock() is an alias for time.clock()
    """
    pytest.debug_func()
    assert abs(nldt.clock() - time.clock()) < 0.0001


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
        nldt.utc_offset(txt['nan'])
    assert txt['utc_offset'] in str(err)


# -----------------------------------------------------------------------------
def test_month_constructor():
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
@pytest.mark.parametrize("month, year, exp", [
    pytest.param(1, None, 31, id="jan"),
    pytest.param(2, 2017, 28, id="feb-common"),
    pytest.param(2, 2016, 29, id='feb-leap'),
    pytest.param(2, 2000, 29, id='feb-400-leap'),
    pytest.param(2, 1900, 28, id='feb-100-common'),
    pytest.param(3, 2018, 31, id='mar'),
    pytest.param(4, None, 30, id='apr'),

    pytest.param(5, None, 31, id='may'),
    pytest.param(6, None, 30, id='june'),
    pytest.param(7, None, 31, id='july'),
    pytest.param(8, None, 31, id='aug'),
    pytest.param(9, None, 30, id='sep'),
    pytest.param(10, None, 31, id='oct'),
    pytest.param(11, None, 30, id='nov'),
    pytest.param(12, None, 31, id='dec'),
    pytest.param(19, None, txt["err-indxfy-nof"], id='ex-range'),
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
def test_month_days():
def test_month_days_curyear():
    """
    Verify that month.days() for february this year does the right thing
    """
    raise nldt.Stub()
    pytest.debug_func()
    mobj = nldt.month()
    now = nldt.moment()
    curyear = int(now('%Y'))
    exp = 29 if mobj.isleap(curyear) else 28
    # payload
    assert mobj.days(2) == exp


# -----------------------------------------------------------------------------
def test_month_under_days():
    """
    """
    pytest.debug_func()
    mobj = nldt.month()
    exp = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    for dnum in range(1, 13):
        assert mobj._days(dnum) == exp[dnum-1]


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
    assert txt['not_indxfy'].format('frobble') in str(err)


# -----------------------------------------------------------------------------
@pytest.mark.parametrize("year, exp", [
    pytest.param(1896, True, id='1896'),
    pytest.param(1899, False, id='1899'),
    pytest.param(1900, False, id='1900'),
    pytest.param(1901, False, id='1901'),
    pytest.param(1904, True, id='1904'),
    pytest.param(1996, True, id='1996'),
    pytest.param(1999, False, id='1999'),
    pytest.param(2000, True, id='2000'),
    pytest.param(2001, False, id='2001'),
    pytest.param(2004, True, id='2004'),
    ])
def test_month_isleap(year, exp):
    """
    month.isleap() returns True when year is a leap year, otherwise False
    """
    pytest.debug_func()
    m = nldt.month()
    assert m.isleap(year) == exp


# -----------------------------------------------------------------------------
def test_month_curyear_isleap():
    """
    When year is not given, isleap should return True if the current year is
    leap, else False
    """
    raise nldt.Stub()
    pytest.debug_func()
    m = nldt.month()
    if m.days(2) == 29:
        # payload
        assert m.isleap(None)
    else:
        # payload
        assert not m.isleap(None)


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
def test_month_short_names():
    """
    month.short_names() is supposed to return a list of three letter lowercase
    month name abbreviations
    """
    pytest.debug_func()
    m = nldt.month()
    for item in m.short_names():
        assert len(item) == 3
        assert item.lower() == item


# -----------------------------------------------------------------------------
def test_month_match_monthnames():
# -----------------------------------------------------------------------------
@pytest.mark.parametrize("inp, exp", [
    pytest.param("No monthnames in this string", None, id='nomatch'),
    pytest.param("January is present here", "January", id='January'),
    pytest.param("This string has February in the middle", "February",
                 id='February'),
    pytest.param("At the end of this string we find March", "March",
                 id='March'),
    pytest.param("Here's April", "April", id='April'),
    pytest.param("We may find a month name here", "may", id='May'),
    pytest.param("See the moon in june", "june", id='June'),
    pytest.param("This is JULY", "JULY", id='July'),
    pytest.param("Augustus was a Roman emperor", "August", id='August'),
    pytest.param("Try to remember the kind of september", "september",
                 id='September'),
    pytest.param("october october october", "october", id='October'),
    pytest.param("Last November was the time", "November", id='November'),
    pytest.param("Winter solstice in December", "December", id='December'),
    ])
def test_month_match_monthnames(inp, exp):
    """
    Test the monthnames regex against each of the month names
    """
    raise nldt.Stub()
    pytest.debug_func()
    m = nldt.month()
    rgx = m.match_monthnames()
    result = re.search(rgx, inp, re.I)
    if exp is None:
        assert result is None
    else:
        assert exp == result.group()


# -----------------------------------------------------------------------------
def test_week_constructor()
def test_week_constructor():
    """
    nldt.week() constructor should return an object with dict of months
    """
    raise nldt.Stub()
    pytest.debug_func()
    w = nldt.week()
    assert hasattr(w, '_dict')
    for midx in range(0, 7):
        assert midx in w._dict
    for wname in ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']:
        assert wname in w._dict


# -----------------------------------------------------------------------------
def test_week_day_list()
def test_week_day_list():
    """
    Verify nldt.week.day_list()
    """
    raise nldt.Stub()
    pytest.debug_func()
    w = nldt.week()
    dl = w.day_list()
    for wname in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday',
                  'Saturday', 'Sunday']:
        assert wname.lower() in dl


# -----------------------------------------------------------------------------
def test_week_find_day()
# -----------------------------------------------------------------------------
@pytest.mark.parametrize("text, exp", [
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
def test_week_find_day(text, exp):
    """
    Coverage for week.find_day()
    """
    raise nldt.Stub()
    pytest.debug_func()
    w = nldt.week()
    assert w.find_day(text) == exp


# -----------------------------------------------------------------------------
def test_week_forediff()
@pytest.mark.parametrize("inps, inpe, exp", [
    pytest.param('mon', 'tue', 1, id='mon-tue'),
    pytest.param('mon', 2, 2, id='mon-wed'),
    pytest.param(0, 'thu', 3, id='mon-thu'),
    pytest.param('mon', 'fri', 4, id='mon-fri'),
    pytest.param(0, 5, 5, id='mon-sat'),
    pytest.param('mon', 'sun', 6, id='mon-sun'),
    pytest.param('mon', 'mon', 7, id='mon-mon'),

    pytest.param('tue', 'wed', 1, id='tue-wed'),
    pytest.param('tue', 3, 2, id='tue-thu'),
    pytest.param(1, 'fri', 3, id='tue-fri'),
    pytest.param(1, 5, 4, id='tue-sat'),
    pytest.param('tue', 'sun', 5, id='tue-sun'),
    pytest.param('tue', 'mon', 6, id='tue-mon'),
    pytest.param('tue', 'tue', 7, id='tue-tue'),

    pytest.param('wed', 'thu', 1, id='wed-thu'),
    pytest.param('wed', 'fri', 2, id='wed-fri'),
    pytest.param('wed', 'sat', 3, id='wed-sat'),
    pytest.param('wed', 'sun', 4, id='wed-sun'),
    pytest.param('wed', 'mon', 5, id='wed-mon'),
    pytest.param('wed', 'tue', 6, id='wed-tue'),
    pytest.param('wed', 'wed', 7, id='wed-wed'),

    pytest.param('thu', 'fri', 1, id='thu-fri'),
    pytest.param('thu', 'sat', 2, id='thu-sat'),
    pytest.param('thu', 'sun', 3, id='thu-sun'),
    pytest.param('thu', 'mon', 4, id='thu-mon'),
    pytest.param('thu', 'tue', 5, id='thu-tue'),
    pytest.param('thu', 'wed', 6, id='thu-wed'),
    pytest.param('thu', 'thu', 7, id='thu-thu'),

    pytest.param(4, 'fri', 7, id='fri-fri'),
    pytest.param(4, 'sat', 1, id='fri-sat'),
    pytest.param(4, 'sun', 2, id='fri-sun'),
    pytest.param(4, 'mon', 3, id='fri-mon'),
    pytest.param(4, 'tue', 4, id='fri-tue'),
    pytest.param(4, 'wed', 5, id='fri-wed'),
    pytest.param(4, 'thu', 6, id='fri-thu'),

    pytest.param('sat', 6, 1, id='sat-sun'),
    pytest.param('sat', 0, 2, id='sat-mon'),
    pytest.param('sat', 1, 3, id='sat-tue'),
    pytest.param('sat', 2, 4, id='sat-wed'),
    pytest.param('sat', 3, 5, id='sat-thu'),
    pytest.param('sat', 4, 6, id='sat-fri'),
    pytest.param('sat', 5, 7, id='sat-sat'),

    pytest.param('sun', 0, 1, id='sun-mon'),
    pytest.param('sun', 1, 2, id='sun-tue'),
    pytest.param('sun', 2, 3, id='sun-wed'),
    pytest.param('sun', 3, 4, id='sun-thu'),
    pytest.param('sun', 4, 5, id='sun-fri'),
    pytest.param('sun', 5, 6, id='sun-sat'),
    pytest.param('sun', 6, 7, id='sun-sun'),
    ])
def test_week_forediff(inps, inpe, exp):
    """
    week.forediff() returns the number of days between two week days, jumping
    forward. The returned value ranges between 1 and 7
    """
    pytest.debug_func()
    w = nldt.week()
    assert w.find_day(text) == exp
    assert w.forediff(inps, inpe) == exp


# -----------------------------------------------------------------------------
@pytest.mark.parametrize("inps, inpe, exp", [
    pytest.param('mon', 'mon', 7, id='mon-mon'),
    pytest.param('mon', 'tue', 6, id='mon-tue'),
    pytest.param('mon', 2, 5, id='mon-wed'),
    pytest.param(0, 'thu', 4, id='mon-thu'),
    pytest.param('mon', 'fri', 3, id='mon-fri'),
    pytest.param(0, 5, 2, id='mon-sat'),
    pytest.param('mon', 'sun', 1, id='mon-sun'),

    pytest.param('tue', 'wed', 6, id='tue-wed'),
    pytest.param('tue', 3, 5, id='tue-thu'),
    pytest.param(1, 'fri', 4, id='tue-fri'),
    pytest.param(1, 5, 3, id='tue-sat'),
    pytest.param('tue', 'sun', 2, id='tue-sun'),
    pytest.param('tue', 'mon', 1, id='tue-mon'),
    pytest.param('tue', 'tue', 7, id='tue-tue'),

    pytest.param('wed', 'thu', 6, id='wed-thu'),
    pytest.param('wed', 'fri', 5, id='wed-fri'),
    pytest.param('wed', 'sat', 4, id='wed-sat'),
    pytest.param('wed', 'sun', 3, id='wed-sun'),
    pytest.param('wed', 'mon', 2, id='wed-mon'),
    pytest.param('wed', 'tue', 1, id='wed-tue'),
    pytest.param('wed', 'wed', 7, id='wed-wed'),

    pytest.param('thu', 'fri', 6, id='thu-fri'),
    pytest.param('thu', 'sat', 5, id='thu-sat'),
    pytest.param('thu', 'sun', 4, id='thu-sun'),
    pytest.param('thu', 'mon', 3, id='thu-mon'),
    pytest.param('thu', 'tue', 2, id='thu-tue'),
    pytest.param('thu', 'wed', 1, id='thu-wed'),
    pytest.param('thu', 'thu', 7, id='thu-thu'),

    pytest.param(4, 'sat', 6, id='fri-sat'),
    pytest.param(4, 'sun', 5, id='fri-sun'),
    pytest.param(4, 'mon', 4, id='fri-mon'),
    pytest.param(4, 'tue', 3, id='fri-tue'),
    pytest.param(4, 'wed', 2, id='fri-wed'),
    pytest.param(4, 'thu', 1, id='fri-thu'),
    pytest.param(4, 'fri', 7, id='fri-fri'),

    pytest.param('sat', 6, 6, id='sat-sun'),
    pytest.param('sat', 0, 5, id='sat-mon'),
    pytest.param('sat', 1, 4, id='sat-tue'),
    pytest.param('sat', 2, 3, id='sat-wed'),
    pytest.param('sat', 3, 2, id='sat-thu'),
    pytest.param('sat', 4, 1, id='sat-fri'),
    pytest.param('sat', 5, 7, id='sat-sat'),

    pytest.param('sun', 0, 6, id='sun-mon'),
    pytest.param('sun', 1, 5, id='sun-tue'),
    pytest.param('sun', 2, 4, id='sun-wed'),
    pytest.param('sun', 3, 3, id='sun-thu'),
    pytest.param('sun', 4, 2, id='sun-fri'),
    pytest.param('sun', 5, 1, id='sun-sat'),
    pytest.param('sun', 6, 7, id='sun-sun'),
    ])
def test_week_backdiff(inps, inpe, exp):
    """
    week.backdiff() returns the number of days between two week days, jumping
    backward. The returned value ranges between 1 and 7
    """
    raise nldt.Stub()
    pytest.debug_func()
    w = nldt.week()
    assert w.backdiff(inps, inpe) == exp


# -----------------------------------------------------------------------------
def test_week_backdiff()
@pytest.mark.parametrize("inp, exp", [
    pytest.param(["Monday", "Mon", "monday", "mon"], 0, id='mon'),
    pytest.param(["Tuesday", "Tue", "tuesday", "tues"], 1, id='tue'),
    pytest.param(["Wednesday", "Wedn", "wednesday", "wednes"], 2, id='wed'),
    pytest.param(["Thursday", "Thur", "thursday", "thu"], 3, id='thu'),
    pytest.param(["Friday", "Fri", "friday", "fri"], 4, id='fri'),
    pytest.param(["Saturday", "Satur", "saturday", "sat"], 5, id='sat'),
    pytest.param(["Sunday", "Sun", "sunday", "sun"], 6, id='sun'),
    ])
def test_week_index(inp, exp):
    """
    Verify that weekday names are mapped to the correct numbers
    """
    raise nldt.Stub()
    pytest.debug_func()
    w = nldt.week()
    for inps in inp:
        assert w.index(inps) == exp


# -----------------------------------------------------------------------------
def test_week_index()
@pytest.mark.parametrize("inpl, exp", [
    pytest.param([0, 'mon', 'mond', 'monday'], "monday", id='mon'),
    pytest.param([1, 'tue', 'tues', 'tuesday'], "tuesday", id='tue'),
    pytest.param([2, 'wed', 'wednes', 'wednesday'], "wednesday", id='wed'),
    pytest.param([3, 'thu', 'thurs', 'thursday'], "thursday", id='thu'),
    pytest.param([4, 'fri', 'frid', 'friday'], "friday", id='fri'),
    pytest.param([5, 'sat', 'satur', 'saturday'], "saturday", id='sat'),
    pytest.param([6, 'sun', 'sunda', 'sunday'], "sunday", id='sun'),
    ])
def test_week_fullname(inpl, exp):
    """
    Verify mapping index and abbreviations to full names
    """
    raise nldt.Stub()
    pytest.debug_func()
    w = nldt.week()
    for inp in inpl:
        assert w.fullname(inp) == exp


# -----------------------------------------------------------------------------
def test_week_fullname()
# !@! Put the strings below into text.py? No... Strings that are purely for
# testing should not be in the production text catalog. But I can create a
# catalog extension file that will import txt from text and then add test
# strings to it.
@pytest.mark.parametrize("inp, exp", [
    pytest.param(txt['rgx_mon'], ["Mon"], id='mon'),
    pytest.param(txt['rgx_tue'], ["Tues"], id='tue'),
    pytest.param(txt['rgx_wed'], ["Wednes"], id='wed'),
    pytest.param(txt['rgx_thu'], ["Thurs", "Satur"], id='thu-sat'),
    pytest.param(txt['rgx_fri'], ["Fri"], id='fri'),
    pytest.param(txt['rgx_sun'], ["Sun"], id='sun'),
    ])
def test_week_match_weekdays(inp, exp):
    """
    Verify that the weekday matching regex works
    """
    raise nldt.Stub()
    pytest.debug_func()
    w = nldt.week()
    assert re.findall(w.match_weekdays(), inp, re.I) == exp


# -----------------------------------------------------------------------------
def test_match_weekdays()
def test_week_day_number():
    """
    Test week.day_number()
    """
    pytest.debug_func()
    w = nldt.week()
    sat = nldt.moment("2000-01-01")
    sun = nldt.moment("2000-01-02")

    assert w.day_number(sat.epoch()) == 5        # payload
    assert w.day_number(sat) == 5                # payload

    with pytest.raises(TypeError) as err:
        # payload
        w.day_number(txt['xpr-tod']) == 14
    assert txt["err-argmore"] in str(err)

    assert w.day_number(sat, count='mon1') == 6    # payload
    assert w.day_number(sun, count='mon1') == 7    # payload

    assert w.day_number(sat, count='sun0') == 6    # payload
    assert w.day_number(sun, count='sun0') == 0    # payload


# -----------------------------------------------------------------------------
def test_tu_constructor():
    """
    Test class time_units constructor
    """
    raise nldt.Stub()
    pytest.debug_func()
    tu = nldt.time_units()
    for unit in ['second', 'minute', 'hour', 'day', 'week', 'month', 'year']:
        assert unit in tu._units


# -----------------------------------------------------------------------------
def test_day_number()
@pytest.mark.parametrize("inp, exp", [
    pytest.param("What 'year' is it?", "year", id='year'),
    pytest.param("The month is march forth", "month", id='month'),
    pytest.param("Next week we'll see what happens", "week", id='week'),
    pytest.param("This is the first day of the rest of time", "day", id='day'),
    pytest.param("Another hour will pass", "hour", id='hour'),
    pytest.param("Wait a minute!", "minute", id='minute'),
    pytest.param("It's the second door on the right", "second", id='second'),
    ])
def test_tu_find_unit(inp, exp):
    """
    Test find_unit() method of class time_units
    """
    raise nldt.Stub()
    pytest.debug_func()
    tu = nldt.time_units()
    assert tu.find_unit(inp) == exp


# -----------------------------------------------------------------------------
def test_tu_constructor()
@pytest.mark.parametrize("inp, exp", [
    pytest.param('second', 1, id='second'),
    pytest.param('minute', 60, id='minute'),
    pytest.param('hour', 3600, id='hour'),
    pytest.param('day', 24 * 3600, id='day'),
    pytest.param('week', 7 * 24 * 3600, id='week'),
    pytest.param('month', 30 * 24 * 3600, id='month'),
    pytest.param('year', 365 * 24 * 3600, id='year'),
    ])
def test_tu_magnitude(inp, exp):
    """
    Test class time_units constructor
    Test magnitude() method of class time_units
    """
    raise nldt.Stub()
    pytest.debug_func()
    tu = nldt.time_units()
    assert tu.magnitude(inp) == exp


# -----------------------------------------------------------------------------
def test_tu_find_unit()
def test_tu_unit_list():
    """
    Verify time_units().unit_list()
    """
    raise nldt.Stub()
    pytest.debug_func()
    tu = nldt.time_units()
    exp = ["second", "minute", "hour", "day", "week", "month", "year"]
    assert list(tu.unit_list()) == exp


# -----------------------------------------------------------------------------
def test_tu_magnitude()
    """
    """
    raise nldt.Stub()


# -----------------------------------------------------------------------------
def test_tu_unit_list()
    """
    """
    raise nldt.Stub()


# -----------------------------------------------------------------------------
    """
    """
    raise nldt.Stub()


# -----------------------------------------------------------------------------
def test_clock()
    """
    """
    raise nldt.Stub()


# -----------------------------------------------------------------------------
def test_local_constructor()
    """
    class local should have a constructor that accepts the name of a timezone,
    calls tzset(), and records the resulting values from
    time.{timezone,altzone,daylight,tzname}
    """
    raise nldt.Stub()


# -----------------------------------------------------------------------------
def test_local_timezone()
    """
    """
    raise nldt.Stub()


# -----------------------------------------------------------------------------
def test_local_altzone()
    """
    """
    raise nldt.Stub()


# -----------------------------------------------------------------------------
def test_local_daylight()
    """
    """
    raise nldt.Stub()


# -----------------------------------------------------------------------------
def test_local_tzname()
    """
    """
    raise nldt.Stub()


# -----------------------------------------------------------------------------
def test_dst()
@pytest.mark.parametrize("zname, std, soff, dst, doff", [
    pytest.param('US/Eastern', 'EST', 18000, 'EDT', 14400, id='est-edt'),
    pytest.param('US/Central', 'CST', 21600, 'CDT', 18000, id='csd-cdt'),
    pytest.param('US/Mountain', 'MST', 25200, 'MDT', 21600, id='mst-mdt'),
    pytest.param('US/Pacific', 'PST', 28800, 'PDT', 25200, id='pst-pdt'),
    pytest.param('Asia/Jakarta', 'WIB', -25200, 'WIB', -25200, id='wib'),
    ])
def test_tz_context_explicit(zname, std, soff, dst, doff):
    """
    Verify that 'with nldt.tz_context(FOOBAR)' creates a context with FOOBAR as
    the local timezone.
    """
    raise nldt.Stub()
    pytest.debug_func()
    with nldt.tz_context(zname):
        assert time.timezone == soff
        assert time.altzone == doff
        assert time.daylight == (soff != doff)
        assert time.tzname == (std, dst)


# -----------------------------------------------------------------------------
def test_timezone()
@pytest.mark.parametrize("zname", pytz.common_timezones)
def test_tz_context(zname):
    """
    Verify that 'with tz_context()' does the right thing for all timezones
    """
    raise nldt.Stub()
    pytest.debug_func()
    offl = nldt.offset_list(zname)
    assert 1 <= len(offl) <= 2
    if 1 == len(offl):
        exp_std = -1 * offl['std']['secs']
        exp_dst = exp_std
    else:
        exp_std = -1 * offl['std']['secs']
        exp_dst = -1 * offl['dst']['secs']
    with nldt.tz_context(zname):
        assert time.timezone == exp_std
        assert time.altzone == exp_dst
        assert time.daylight == (exp_std != exp_dst)


# -----------------------------------------------------------------------------
def test_timegm()
def test_tz_context_default():
    """
    Test default timezone context
    """
    raise nldt.Stub()
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
def test_tz_context()
def test_tz_context_nested():
    """
    Test nested timezone contexts
    """
    raise nldt.Stub()
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
def test_tzname()
    """
    """
    raise nldt.Stub()


# -----------------------------------------------------------------------------
def test_tzset()
    """
    """
    raise nldt.Stub()


# -----------------------------------------------------------------------------
def test_tzstring()
    """
    """
    raise nldt.Stub()


# -----------------------------------------------------------------------------
def test_word_before()
    """
    """
    raise nldt.Stub()



