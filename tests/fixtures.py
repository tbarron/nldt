"""
nldt - Natural Language Date/Time support
Copyright (c) 2017 - <the end of time>  Tom Barron
See file LICENSING for details

This file contains code for testing nldt functionality.
"""
from nldt import moment as M
import nldt
import numbers
import pytest
import re
from nldt.text import txt
import time
import tbx


# -----------------------------------------------------------------------------
def local_formatted(fmt, epoch=None, dstor=None):
    """
    Format the epoch time as local
    """
    dstor = dstor or time.localtime
    return time.strftime(fmt, dstor(epoch))


# -----------------------------------------------------------------------------
def ftime(fmt, local=True, anchor=None):
    """
    Provide an oracle for test_cmdline
    """
    point = nldt.moment(anchor)
    if local:
        tm = time.localtime(point.epoch())
    else:
        tm = time.gmtime(point.epoch())
    rval = time.strftime(fmt, tm)
    return rval


# -----------------------------------------------------------------------------
@pytest.fixture(autouse=True)
def fx_calls_debug(request):
    """
    This fixture fails if the target test does not call pytest.debug_func()
    """
    if 'debug_func' not in request.function.__code__.co_names:
        pytest.fail("Test '{}' does not call pytest.debug_func"
                    "".format(request.function.__code__.co_name))


# -----------------------------------------------------------------------------
@pytest.fixture
def fx_git_last_tag():
    """
    Determine and return the latest git tag
    """
    result = tbx.run("git --no-pager tag --sort=taggerdate")
    tag_l = result.strip().split("\n")
    latest_tag = tag_l[-1] if 0 < len(tag_l) else ""
    return latest_tag


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
    if spec == txt["xpr-4dotw"]:
        now = prs(txt["xpr-lwk"])
        now = prs(txt["xpr-nwk"], now)
        now = prs(txt["xpr-nthu"], now)
        return now(otz='utc')
    elif spec == txt["xpr-5dolw"]:
        now = nldt.moment(txt["xpr-lwk"])
        now.parse(txt["xpr-nfri"])
        return now(otz='utc')
    elif spec == 'today':
        return local_formatted(txt['iso_date'], None, time.gmtime)
    elif spec == 'tomorrow':
        tm = time.gmtime()
        then = M(time.mktime((tm.tm_year, tm.tm_mon, tm.tm_mday+1,
                              0, 0, 0, 0, 0, 0)))
        return then(otz='utc')
    elif spec == 'yesterday':
        tm = time.gmtime()
        then = M(time.mktime((tm.tm_year, tm.tm_mon, tm.tm_mday-1,
                              0, 0, 0, 0, 0, 0)))
        return then(otz='utc')
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
            return nmon(otz='utc')
        elif nldt.word_before('month', spec) == 'last':
            tm = time.gmtime()
            lmon = M(time.mktime((tm.tm_year, tm.tm_mon-1, 1,
                                  0, 0, 0, 0, 0, 0)))
            return lmon(otz='utc')
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
        return start(otz='utc')
    elif spec == 'last week':
        wdidx = wk.index('mon')
        start = prs('yesterday')
        start = nldt.moment(start.epoch() - 6*24*3600)
        while wk.day_number(start) != wdidx:
            start = prs('yesterday', start)
        return start(otz='utc')
    elif spec == 'end of the week':
        wdidx = 6
        start = nldt.moment()
        while wk.day_number(start) != wdidx:
            start = prs('tomorrow', start)
        return start(otz='utc')
    elif spec == 'end of last week':
        eolw = M(nldt.moment().week_floor().epoch() - 1)
        return eolw(otz='utc')
    elif spec == 'beginning of next week':
        wdidx = 0
        start = prs('tomorrow')
        while wk.day_number(start) != wdidx:
            start = prs('tomorrow', start)
        return start(otz='utc')
    elif spec == 'first week in last January':
        wdidx = 1
        now = nldt.moment()
        year = now('%Y')
        start = nldt.moment('{}-01-07'.format(year))
        while int(start('%u')) != wdidx:
            start.parse('yesterday')
        return start(otz='utc')
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
        return then(otz='utc')
    elif spec == 'two weeks ago':
        now = nldt.moment()
        then = nldt.moment(now.epoch() - 14 * 24 * 3600)
        return then(otz='utc')
    elif spec == 'three weeks from now':
        now = nldt.moment()
        then = nldt.moment(now.epoch() + 21 * 24 * 3600)
        return then(otz='utc')
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
            return start(otz='utc')
        else:
            now = nldt.moment()
            return now(otz='utc')
    elif re.findall('weeks?', spec) and 'earlier' in spec:
        result = nldt.numberize.scan(spec)
        if isinstance(result[0], numbers.Number):
            mult = result[0]
        else:
            mult = 1
        now = nldt.moment()
        then = nldt.moment(now.epoch() - mult * 7 * 24 * 3600)
        return then(otz='utc')
    elif re.findall('weeks?', spec) and 'later' in spec:
        result = nldt.numberize.scan(spec)
        if isinstance(result[0], numbers.Number):
            mult = result[0]
        else:
            mult = 1
        now = nldt.moment()
        then = nldt.moment(now.epoch() + mult * 7 * 24 * 3600)
        return then(otz='utc')

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
        # now direction is 'week' and day is likely a weekday (eg, from 'monday
        # week')
        #
        # we've already handled '{next,last} week' above, so we don't need to
        # worry about those here
        #
        # weekday we want to advance to
        wdidx = wk.index(day)
        # current time plus a day
        when = time.time() + 24*3600
        while wk.day_number(when) != wdidx:
            # add a day until we hit the target weekday number
            when += 24*3600

        # now jump forward a week
        start = M(when + tu.magnitude('week'))

    return start(otz='utc')
