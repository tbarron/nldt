"""
nldt - Natural Language Date/Time support
Copyright (c) 2017 - <the end of time>  Tom Barron
See file LICENSING for details

This file contains code for testing nldt functionality.
"""
from fixtures import fx_calls_debug    # noqa
from fixtures import nl_oracle
# from tzlocal import get_localzone
# from datetime import datetime
import numbers
import os
import pytest
# import pytz
from nldt.text import txt
import time
import nldt
from nldt import moment as M

nldt.moment.default_tz('clear')


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
    assert txt['not_indxfy'].format('frobble') in str(err)


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
def test_parse_unbound_local():
    """
    An unparseable input is causing a traceback
    """
    pytest.debug_func()
    inp = "one two"
    prs = nldt.Parser()
    with pytest.raises(nldt.ParseError) as err:
        prs(inp)
    assert txt['err_notatime'].format(inp) in str(err)
    assert txt['exc-ulerr'] not in str(err)


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
    eoy = nldt.moment(txt['2010-end'])
    assert not hasattr(eoy, 'parse')
    prs = nldt.Parser()
    result = prs('tomorrow', start=eoy)
    assert result() == txt['2011-begin']
    feb28 = nldt.moment(txt['leap-yester'])
    result = prs('tomorrow', start=feb28)
    assert result() == txt['leap-today']


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
@pytest.mark.parametrize("inp, exp", [
    pytest.param(3.4, 3, id='numfloat'),
    pytest.param(11, 11, id='numint'),
    pytest.param(17, ValueError(txt['err-indxfy'].format(17)),
                 id='year-range'),
    pytest.param('5', 5, id='numstr'),
    pytest.param('October', 10, id='str'),
    pytest.param('oct', 10, id='abbr'),
    ])
def test_month_indexify(inp, exp):
    """
    Tests for month.indexify()
    """
    pytest.debug_func()
    mon = nldt.month()
    if isinstance(exp, Exception):
        with pytest.raises(type(exp)):
            assert mon.indexify(inp) == 'something'
    else:
        assert mon.indexify(inp) == exp


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
    assert txt["err_indxfy"].format("17") in str(err)


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
    assert txt["err-nounit"] in str(err)


# -----------------------------------------------------------------------------
def test_from_now_except():
    """
    Cover the ValueError exception in parse_ago
    """
    pytest.debug_func()
    prs = nldt.Parser()
    with pytest.raises(ValueError) as err:
        prs("no number no unit from now")
    assert txt["err-nounit"] in str(err)


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
        assert txt["err-indxfy-f"].format(inp) in str(err)
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
@pytest.mark.parametrize("tz, exp", [
    pytest.param("Pacific/Norfolk", "XXX-11:00:00", id='Norfolk'),
    pytest.param("Pacific/Pago_Pago", "SST11:00:00", id='Pago_Pago'),
    pytest.param("Pacific/Marquesas", "XXX09:30:00", id='Marquesas'),
    pytest.param("NZ-CHAT", "XXX-12:45:00XXX-13:45:00", id='NZ-CHAT'),
    ])
def test_tzstring(tz, exp):
    """
    tzstring for 'Pacific/Norfolk' should be 'XXX-11:30:00'
    """
    pytest.debug_func()
    assert nldt.tzstring(tz) == exp


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
