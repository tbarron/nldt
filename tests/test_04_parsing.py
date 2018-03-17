"""
nldt - Natural Language Date/Time support
Copyright (c) 2017 - <the end of time>  Tom Barron
See file LICENSING for details

This file contains code for testing nldt functionality.
"""
# class Parser
from fixtures import nl_oracle
from nldt import moment as M
import nldt
import pytest
import time
from nldt.text import txt


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
def test_parse_unbound_local():
    """
    An unparseable input is causing a traceback
    """
    pytest.debug_func()
    inp = "one two"
    prs = nldt.Parser()
    with pytest.raises(nldt.ParseError) as err:
        prs(inp)
    assert txt['err-notatime'].format(inp) in str(err)
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
