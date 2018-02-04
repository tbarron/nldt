"""
Natural Language Date and Time package

This module provides a simple natural language interfaace to Python's time and
date processing machinery.
"""
from calendar import timegm
from datetime import datetime
import numberize
import numbers
from tzlocal import get_localzone
import pytz
import re
import time


# -----------------------------------------------------------------------------
class Indexable(object):
    """
    This class has a _dict dictionary member and a method called indexify that
    will take an argument that may be a number or string and return a numeric
    index for one of the members of _dict. This class is intended as an
    abstract base class for week and month.
    """
    # -------------------------------------------------------------------------
    def indexify(self, name_or_idx):
        """
        Return an int idx in the range [0, 7) (i.e., between 0 and 6 inclusive)
        or -1.
        """
        rval = None
        if name_or_idx in self._dict:
            rval = self._dict[name_or_idx]['idx']
        elif isinstance(name_or_idx, str):
            name_or_idx = name_or_idx.lower()
            if name_or_idx.isdigit():
                idx = int(name_or_idx)
                if idx in self._dict:
                    rval = self._dict[idx]['idx']
            elif 3 < len(name_or_idx):
                abbr = name_or_idx.lower()[0:3]
                if abbr in self._dict:
                    rval = self._dict[abbr]['idx']
            elif name_or_idx in self._dict:
                rval = self._dict[name_or_idx]['idx']
        elif isinstance(name_or_idx, numbers.Number):
            if int(name_or_idx) in self._dict:
                rval = self._dict[int(name_or_idx)]['idx']
        if rval is None:
            raise ValueError("Could not indexify '{}'".format(name_or_idx))
        return rval


# -----------------------------------------------------------------------------
def dst(when=None, tz=None):
    """
    Return True or False - daylight savings time is in force or not

    Examples:
        >>> import nldt
        >>> nldt.dst()
        False
    """
    when = when or moment("2010-01-01")
    if isinstance(when, numbers.Number) or isinstance(when, str):
        when = moment(when)
    if not isinstance(when, moment):
        raise TypeError("dst() when arg must be str, number, or moment")

    tz = tz or 'local'
    if tz == 'local':
        tm = time.localtime(when.moment)
    else:
        tm = time.gmtime(when.moment + utc_offset(when.moment, tz))

    return tm.tm_isdst == 1


# -----------------------------------------------------------------------------
def hhmm(seconds):
    """
    Returns a string showing HHMM based on *seconds*
    """
    prefix = ""
    if seconds < 0:
        prefix = "-"
        seconds = -1 * seconds
    mins = int(seconds / 60)
    hrs = int(mins / 60)
    mins = mins % 60
    return "{}{:02d}{:02d}".format(prefix, hrs, mins)


# -----------------------------------------------------------------------------
def parse(expr, start=None):
    """
    Returns a moment based on *expr* and *start*, if provided. If *start* is
    not provided, the current UTC time is used.
    """
    start = start or moment()
    wk = week()
    mon = month()
    tu = time_units()
    wkdays_rgx = wk.match_weekdays()
    rval = None
    result = []

    expr = expr.replace('earlier', 'ago')
    expr = expr.replace('later', 'from now')

    if research("\s(of|in)\s", expr, result):
        rval = parse_of_in(expr, result[0].group())
    elif expr.strip().lower() in mon.names():
        rval = parse_month_name(expr)
    elif expr == 'today':
        rval = moment()
    elif expr == 'tomorrow':
        rval = moment(start.moment + tu.magnitude('day'))
    elif expr == 'yesterday':
        rval = moment(start.moment - tu.magnitude('day'))
    elif 'ago' in expr:
        rval = parse_ago(expr)
    elif 'from now' in expr:
        rval = parse_from_now(expr)
    elif re.search("(\s|^)month(\s|$)", expr):
        rval = parse_month(expr, start)
    elif re.search("(\s|^)week(\s|$)", expr):
        wb = word_before('week', expr)
        if wb == 'last':
            rval = moment(start.week_floor().epoch() - tu.magnitude('week'))
        elif wb == 'next':
            rval = moment(start.week_floor().epoch() + tu.magnitude('week'))
        elif wb == 'first':
            tm = start.gmtime()
            delta = (7 - tm.tm_wday) % 7
            rval = moment(timegm((tm.tm_year, tm.tm_mon, tm.tm_mday + delta,
                                  0, 0, 0, 0, 0, 0)))
        elif wb == 'the' or wb == 'this':
            rval = start.week_floor()
        elif wb in wk.day_list():
            start = parse('next {}'.format(wb))
            rval = parse('next {}'.format(wb), start)
        elif expr == 'week after next':
            rval = parse('next week')
            rval = parse('next week', rval)
        elif expr == 'week before last':
            rval = parse('last week')
            rval = parse('last week', rval)
    elif re.search("(\s|^)year(\s|$)", expr):
        wb = word_before('year', expr)
        if wb == 'last':
            then = "{}-01-01".format(int(start("%Y")) - 1)
            rval = moment(then)
        elif wb == 'next':
            then = "{}-01-01".format(int(start("%Y")) + 1)
            rval = moment(then)
    elif research(wkdays_rgx, expr, result):
        wday = result[0].group()
        wb = word_before(wday, expr)
        if wb == 'next':
            swd = start('%A').lower()
            delta = wk.forediff(swd, wday) or 7
            rval = moment(start.epoch() + delta * tu.magnitude('day'))
        elif wb == 'last':
            swd = start('%A').lower()
            delta = wk.backdiff(swd, wday) or 7
            rval = moment(start.epoch() - delta * tu.magnitude('day'))
    return rval


# -----------------------------------------------------------------------------
def parse_ago(expr):
    """
    Handle expressions like 'a week ago', 'three days ago', 'five years ago',
    etc.
    """
    tu = time_units()
    nums = numberize.scan(expr)
    if isinstance(nums[0], int):
        count = nums[0]
    else:
        count = 1
    unit = tu.find_unit(expr)
    if unit is None:
        raise ValueError("No unit found in expression '{}'".format(expr))
    rval = moment()
    rval = moment(rval.epoch() - count * tu.magnitude(unit))
    return rval


# -----------------------------------------------------------------------------
def parse_from_now(expr):
    """
    Handle expressions like 'an hour from now', 'two days from now', 'four
    weeks from now', 'three years from now', etc.
    """
    tu = time_units()
    nums = numberize.scan(expr)
    if isinstance(nums[0], int):
        count = nums[0]
    else:
        count = 1
    unit = tu.find_unit(expr)
    if unit is None:
        raise ValueError("No unit found in expression '{}'".format(expr))
    rval = moment()
    rval = moment(rval.epoch() + count * tu.magnitude(unit))
    return rval


# -----------------------------------------------------------------------------
def parse_month(expr, start):
    """
    Handle 'next month', 'last month'
    """
    tu = time_units()
    wb = word_before('month', expr)
    if wb == 'last':
        day_mag = tu.magnitude('day')
        rval = moment(start.month_floor().epoch() - day_mag).month_floor()
    elif wb == 'next':
        week_mag = tu.magnitude('week')
        rval = moment(start.month_ceiling().epoch() + week_mag).month_floor()
    return rval


# -----------------------------------------------------------------------------
def parse_month_name(expr):
    """
    Parse a string recognized as the name of a month
    """
    mon = month()
    rval = moment()
    tm = rval.gmtime()
    midx = mon.index(expr)
    return moment((tm.tm_year, midx, 1, 0, 0, 0, 0, 0, 0))


# -----------------------------------------------------------------------------
def parse_of_in(expr, prep):
    """
    Parse expressions like 'first week in January', 'last day of April', etc.
    """
    tu = time_units()
    unit = tu.find_unit(expr)
    pre, post = expr.split(prep)
    rval = parse(post)
    if pre == 'end' and unit:
        rval = rval.ceiling(unit)
    elif pre == 'beginning':
        pass
    else:
        rval = parse(pre, rval)
    return rval


# -----------------------------------------------------------------------------
def research(pattern, haystack, result):
    """
    Look for pattern in haystack. If something is found, push the search object
    into result (which much be a list) and return it
    """
    q = re.search(pattern, haystack)
    if q:
        result.append(q)
    return q


# -----------------------------------------------------------------------------
def word_before(item, text):
    """
    Parse out the word that occurs before *item* in *text* and return it
    """
    next = False
    for word in reversed(text.split()):
        if next:
            return word
        if word == item:
            next = True
    return None


# -----------------------------------------------------------------------------
def timezone():
    """
    Returns the locally configured timezone name

    The timezone may vary with whether DST is in effect or not. The example
    show a timezone of 'EST' for Eastern Standard Time. At times of the year
    when DST is in effect, the timezone is EDT.

    Examples:
        >>> import nldt
        >>> nldt.timezone
        EST
    """
    now = time.localtime()
    rval = time.tzname[now.tm_isdst]
    return rval


# -----------------------------------------------------------------------------
def utc_offset(epoch=None, tz=None):
    """
    Returns the number of seconds to add to UTC to get local time. If epoch is
    not provided, the current time is used. If tz is not provided, the local
    timezone is used. Account is taken of daylight savings time for the
    indicated timezone and epoch.
    """
    epoch = epoch or time.time()
    if not isinstance(epoch, numbers.Number):
        raise TypeError("utc_offset requires an epoch time or None")

    tz = tz or 'local'
    if tz == 'local':
        zone = get_localzone()
    else:
        zone = pytz.timezone(tz)

    offset = zone.utcoffset(datetime.fromtimestamp(epoch))
    return offset.total_seconds()


# -----------------------------------------------------------------------------
_WEEKDAYS = {'mon': 0, 0: 'monday',
             'tue': 1, 1: 'tuesday',
             'wed': 2, 2: 'wednesday',
             'thu': 3, 3: 'thursday',
             'fri': 4, 4: 'friday',
             'sat': 5, 5: 'saturday',
             'sun': 6, 6: 'sunday'}

_MONTHS = {'jan': 1, 1: 'january',
           'feb': 2, 2: 'february',
           'mar': 3, 3: 'march',
           'apr': 4, 4: 'april',
           'may': 5, 5: 'may',
           'jun': 6, 6: 'june',
           'jul': 7, 7: 'july',
           'aug': 8, 8: 'august',
           'sep': 9, 9: 'september',
           'oct': 10, 10: 'october',
           'nov': 11, 11: 'november',
           'dec': 12, 12: 'december',
           }

_MONTH_LEN = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]


# -----------------------------------------------------------------------------
class month(Indexable):     # I managed to lose this update
    """
    Defines and serves information about months
    """
    # -------------------------------------------------------------------------
    def __init__(self):
        """
        Set up month info
        """
        self._dict = {}
        for midx in range(1, 13):
            date = "2010.{:02d}01".format(midx)
            q = moment(date)
            mname = q('%B').lower()
            abbr = mname[0:3]
            this = {
                'name': mname,
                'abbr': abbr,
                'idx': midx,
                'days': self._days(midx)
                }
            self._dict[abbr] = this
            self._dict[midx] = this

    # -------------------------------------------------------------------------
    def days(self, month, year=None):
        month = self.indexify(month)              # noqa: F821
        rval = self._dict[month]['days']
        if month == 2 and self.isleap(year):
            rval += 1
        return rval

    # -------------------------------------------------------------------------
    def _days(self, midx):
        q = moment("2010.{:02d}01".format((midx % 12) + 1))
        p = moment(q.moment - 24 * 3600)
        rval = int(p('%d'))
        return rval

    # -------------------------------------------------------------------------
    def index(self, name_or_idx):
        """
        Given a month name or index in *name_or_idx*, this returns the index of
        the month or throws a ValueError.
        """
        midx = self.indexify(name_or_idx)
        return self._dict[midx]['idx']

    # -------------------------------------------------------------------------
    def isleap(self, year):
        if year is None:
            rval = False
        else:
            rval = (year % 4 == 0 and year % 100 != 0) or year % 400 == 0
        return rval

    # -------------------------------------------------------------------------
    def names(self):
        return [self._dict[x]['name'] for x in self._dict
                if isinstance(x, int)]

    # -------------------------------------------------------------------------
    def short_names(self):
        return [self._dict[x]['abbr'] for x in self._dict
                if isinstance(x, int)]

    # -------------------------------------------------------------------------
    def match_monthnames(self):
        """
        Return a regex that will match all month names
        """
        rgx = "(" + "|".join([self._dict[x]['name'] for x in self._dict
                              if isinstance(x, int)]) + ")"
        return rgx


# -----------------------------------------------------------------------------
class week(Indexable):
    """
    Define and serve weekday information
    """
    # -------------------------------------------------------------------------
    def __init__(self):
        """
        Set up week info
        """
        self._dict = {}
        for idx in range(0, 7):
            q = moment("2018.01{:02d}".format(idx+1))
            wname = q('%A').lower()
            abbr = wname[0:3]
            this = {
                'name': wname,
                'abbr': abbr,
                'idx': idx,
                }
            self._dict[abbr] = this
            self._dict[idx] = this

    # -------------------------------------------------------------------------
    def day_list(self):
        """
        Return a list of weekday names
        """
        return [self._dict[x]['name'] for x in self._dict
                if isinstance(x, int)]

    # -------------------------------------------------------------------------
    def find_day(self, text):
        """
        Find and return the first weekday name in *text*
        """
        found = [wday for wday in self.day_list()
                 if re.search("(^|\W){}(\W|$)".format(wday), text)]
        if found:
            return found[0]
        else:
            return None

    # -------------------------------------------------------------------------
    def forediff(self, start, end):
        """
        Return the number of days required to get from day *start* to day *end*
        going forward. *start* and *end* can be day names or index values.
        """
        start = self.indexify(start)
        end = self.indexify(end)
        if end <= start:
            end += 7
        rval = end - start
        return rval

    # -------------------------------------------------------------------------
    def backdiff(self, start, end):
        """
        Return the number of days required to get from day *start* to day *end*
        going forward. *start* and *end* can be day names or index values.
        """
        start = self.indexify(start)
        end = self.indexify(end)
        if start <= end:
            start += 7
        rval = start - end
        return rval

    # -------------------------------------------------------------------------
    def index(self, wday):
        """
        Return the numeric index for *wday* (sun = 0, mon = 1, ... sat = 6)
        """
        if 3 < len(wday):
            wday = wday[0:3].lower()
        rval = self._dict.get(wday, -1)
        return rval['idx']

    # -------------------------------------------------------------------------
    def fullname(self, idx_or_abbr):
        """
        Look up *idx_or_abbr* in self._dict and return the 'name' item
        """
        idx = self.indexify(idx_or_abbr)
        return self._dict[idx]['name']

    # -------------------------------------------------------------------------
    def match_weekdays(self):
        """
        Return a regex that will match all weekdays
        """
        return "(mon|tues|wednes|thurs|fri|satur|sun)day"

    # -------------------------------------------------------------------------
    def day_number(self, moment_or_epoch, count=None):
        """
        This returns a weekday number based on a moment or epoch time. The
        *count* argument can be one of 'mon0' (the default), 'sun0', or 'mon1'.
        With 'mon0', mon=0 and sun=6. With sun0, sun=0 and sat=6. With mon1,
        mon=1 and sun=7. mon0 is the counting regime used in the tm structures
        returned by time.localtime() and time.gmtime(). sun0 is the counting
        regime for the '%w' specifier in time.strftime() and time.strptime()
        patterns. mon1 is the counting regime for the '%u' specifier in
        time.strftime() and time.strptime().
        """
        count = count or 'mon0'
        if isinstance(moment_or_epoch, moment):
            epoch = moment_or_epoch.epoch()
        elif isinstance(moment_or_epoch, numbers.Number):
            epoch = moment_or_epoch
        else:
            raise TypeError('argument must be moment or epoch number')
        tm = time.gmtime(epoch)
        if count == 'mon0':
            return tm.tm_wday
        elif count == 'mon1' or count == '%u':
            return tm.tm_wday + 1
        elif count == 'sun0' or count == '%w':
            return (tm.tm_wday + 1) % 7


# -----------------------------------------------------------------------------
def month_days(month):
    """
    Given a month name, this returns the number of days in the month for the
    current year

    *month* - three+ letter month name string => int between 1 (jan) and 12
              (dec)

    Example:
        >>> nldt.month_days('January')
        31
        >>> nldt.month_days('febr')
        28
        >>> nldt.month_days('september')
        30
        >>> nldt.month_days('dec')
        31
    """
    idx = month.lower()[0:3]
    mdx = _MONTHS[idx]
    rval = _MONTH_LEN[mdx-1]
    return rval


# -----------------------------------------------------------------------------
def month_index(month):
    """
    Given month name, return index (January == 1; December == 12)

    *month* - three+ letter month name string => int between 1 (jan) and 12
              (dec)

    Example:
        >>> nldt.month_index('January')
        1
        >>> nldt.month_index('febr')
        2
    """
    idx = month.lower()[0:3]
    rval = _MONTHS[idx]
    return rval


# -----------------------------------------------------------------------------
def month_names():
    """
    Return the list of month names in order

    Example:
        >>> nldt.month_names()
        ['january', 'february', 'march', 'april', 'may', 'june',
         'july', 'august', 'september', 'october', 'november', 'december']
    """
    ikeys = sorted(_ for _ in _MONTHS if isinstance(_, int))
    rval = [_MONTHS[_] for _ in ikeys]
    return rval


# -----------------------------------------------------------------------------
def weekday_index(weekday):
    """
    Given weekday name, return index (Monday == 0; Sunday == 6)

    *weekday* - int between 0 and 6 => three letter day name string
                three letter day name string => int between 0 (mon) and 6 (sun)

    Example:
        >>> import nldt

        # Compute weekday delta
        >>> diff = nldt.weekday_index('thu') - nldt.weekday_index('mon')

        # diff == number of days to jump from monday to thursday
        >>> diff = nldt.weekday_index('mon') - nldt.weekday_index('thu')

        # diff == number of days to jump from thursday to monday (negative)
        # General:
        >>> diff = nldt.weekday_index(end_day) - nldt.weekday_index(start_day)
        # diff == days to jump from start to end, either forward or backward
        # 7 + diff == days to jump from start to end in succeeding week
    """
    idx = weekday.lower()[0:3]
    rval = _WEEKDAYS[idx]
    return rval


# -----------------------------------------------------------------------------
def weekday_names():
    """
    Return the list of weekday names in order

    *weekday* - int between 0 and 6 => three letter day name string
                three letter day name string => int between 0 (mon) and 6 (sun)

    Example:
        >>> import nldt

        # Get the list
        >>> nldt.weekday_names()
        ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday',
        'sunday']
    """
    ikeys = sorted(_ for _ in _WEEKDAYS if isinstance(_, int))
    rval = [_WEEKDAYS[_] for _ in ikeys]
    return rval


# -----------------------------------------------------------------------------
class prepositions(object):
    """
    Provide information and tools for finding and interpreting prepositions in
    natural language time expressions
    """
    # -------------------------------------------------------------------------
    def __init__(self):
        """
        Set up the prepositions object. In the self.preps dict, the keys are
        the recognized prepositions and the values indicate the temporal
        direction of the key -- +1 for forward in time, -1 for backward.
        """
        self.preps = {'of': 1, 'in': 1, 'from': 1, 'after': 1, 'before': -1}

    # -------------------------------------------------------------------------
    def split(self, text):
        """
        Construct (and cache) a regex based on the prepositions and use it to
        split *text*, returning the list of pieces.
        """
        if not hasattr(self, 'regex'):
            self.regex = "\\s(" + "|".join(self.preps.keys()) + ")\\s"
        rval = re.split(self.regex, text)
        return rval[1], rval

    # -------------------------------------------------------------------------
    def are_in(self, text):
        """
        Returns True if *text* contains any prepositions
        """
        return any([x in self.preps for x in text.split()])

    # -------------------------------------------------------------------------
    def direction(self, prep):
        """
        Return the direction for preposition *prep*
        """
        return self.preps[prep]


# -----------------------------------------------------------------------------
class time_units(object):
    """
    Provide information about time units
    """
    # -------------------------------------------------------------------------
    def __init__(self):
        """
        Sets up the list of units with the number of seconds in each
        """
        self.units = {'second': 1,
                      'minute': 60,
                      'hour': 3600,
                      'day': 24 * 3600,
                      'week': 7 * 24 * 3600,
                      'month': 30 * 24 * 3600,
                      'year': 365 * 24 * 3600}

    # -------------------------------------------------------------------------
    def find_unit(self, text):
        """
        Scans *text* and return the first unit found or None
        """
        found = [unit for unit in self.units.keys()
                 if re.search("(^|\s){}s?(\s|$)".format(unit), text)]
        if found:
            return found[0]
        else:
            return None

    # -------------------------------------------------------------------------
    def magnitude(self, unit):
        """
        Returns the number of seconds in *unit* or -1 if *unit* is not valid
        """
        return self.units.get(unit, -1)

    # -------------------------------------------------------------------------
    def unit_list(self):
        """
        Returns the list of units
        """
        return self.units.keys()

    # -------------------------------------------------------------------------
    # def parse(self, spec):
    #     """
    #     Set the object's value to the date/time indicated by *spec*
    #
    #     *spec* - A date/time specification in a string, possibly natural
    #              language
    #
    #     Calculations are relative to the CSM (see the example -- after
    #     parsing '2013.0630', the calculation of 'next friday' is relative to
    #     2013-06-30, not to the present moment)
    #
    #     Example:
    #         >>> import nldt
    #         >>> foo = nldt.moment()
    #         >>> foo.parse('next friday')
    #         >>> foo()
    #         '2016-12-09'
    #         >>> foo.parse('2013.0630')
    #         >>> foo.parse('next friday')
    #         >>> foo()
    #         '2013-07-05'
    #     """
    #     self.moment = self._parse_return(spec)

    # -------------------------------------------------------------------------
    # def _nl_match(self, spec):
    #     """
    #     Look for matches for *spec* in the natural lanugage dictionary
    #
    #     Example:
    #         >>> function = self._nl_match('first week in January')
    #         >>> function
    #         <bound method '_first_week_in'>
    #     """
    #     self.spec = spec
    #     if spec in self.nldict:
    #         rval = getattr(self, self.nldict[spec])
    #         return rval
    #     for key in self.nldict:
    #         if key in spec:
    #             rval = getattr(self, self.nldict[key])
    #             return rval
    #     return None

    # -------------------------------------------------------------------------
    # nldict = {'end of last week': '_end_of_last_week',
    #           'last week': '_last_week',
    #           'the week': '_this_week',
    #           'this week': '_this_week',
    #           'first week in': '_first_week_in_MONTH',
    #           'start of next week': '_start_of_next_week',
    #           'week from now': '_week_from_now',
    #           'tomorrow': '_tomorrow',
    #           'week after next': '_week_after_next',
    #           'week ago': '_week_ago',
    #           'week before last': '_week_before_last',
    #           'week earlier': '_week_ago',
    #           'week later': '_week_from_now',
    #           'yesterday': '_yesterday',
    #           }

    # -------------------------------------------------------------------------
    # def _parse_return(self, spec):
    #     """
    #     Figure out what spec means -- the heavy lift of parsing
    #
    #     spec - A date/time specification
    #
    #     Example:
    #         foo = when.when()
    #         foo.parse('2013.0630')
    #         foo.parse('next friday at 5')
    #
    #     internal
    #     """
    #     rval = self._guess_format(spec)
    #     if rval is not None:
    #         return rval
    #
    #     spec = spec.replace('beginning', 'start')
    #     spec = spec.replace('weeks', 'week')
    #
    #     if spec.lower()[0:3] in _MONTHS:
    #         mon_yr = "{} {}".format(spec.lower()[0:3], time.strftime("%Y"))
    #         rval = time.mktime(time.strptime(mon_yr, "%B %Y"))
    #         return rval
    #
    #     preps = prepositions()
    #     if preps.are_in(spec):
    #         tu = time_units()
    #         prep, pieces = preps.split(spec)
    #         signum = preps.direction(prep)
    #         base = self._parse_return(pieces[-1])
    #         nums = numberize.scan(pieces[0])
    #         unit = tu.find_unit(pieces[0])
    #         if unit and nums:
    #             rval = (base + signum * nums[0] * tu.magnitude(unit))
    #         elif unit:
    #             rval = base + signum * tu.magnitude(unit)
    #         else:
    #             rval = self._interpret(base, pieces)
    #         return rval
    #
    #     func = self._nl_match(spec)
    #     if func:
    #         return func(spec=spec)
    #
    #     weekday_rgx = '(mon|tue|wed|thu|fri|sat|sun)'
    #     if spec == 'yesterday':
    #         ref = self.moment or time.time()
    #         yest = ref - _DAY
    #         rval = yest - yest % (_DAY) + time.timezone
    #     elif 'end of' in spec:
    #         ml = re.findall(weekday_rgx, spec)
    #         if ml:
    #             rval = self.end_of_day(ml[0])
    #         elif 'last week' in spec:
    #             now = self.moment or time.time()
    #             tmp = moment(now - 7 * _DAY)
    #             rval = tmp._end_of_week()
    #         elif 'week' in spec:
    #             rval = self._end_of_week()
    #         elif 'month' in spec:
    #             rval = self._end_of_month()
    #         elif 'year' in spec:
    #             rval = self._end_of_year()
    #     elif 'next' in spec:
    #         ml = re.findall(weekday_rgx, spec)
    #         if ml:
    #             rval = self._next_weekday(ml[0])
    #         else:
    #             if 'week' in spec:
    #                 rval = self._next_weekday('mon')
    #             elif 'month' in spec:
    #                 rval = self._next_month()
    #             elif 'year' in spec:
    #                 rval = self._next_year()
    #     elif 'last' in spec:
    #         ml = re.findall(weekday_rgx, spec)
    #         if ml:
    #             rval = self._last_weekday(ml[0])
    #         else:
    #             if 'week' in spec:
    #                 tmp = moment(time.time() - 7*_DAY)
    #                 rval = tmp._last_weekday('mon')
    #             elif 'month' in spec:
    #                 rval = self._last_month()
    #             elif 'year' in spec:
    #                 rval = self._last_year()
    #     elif spec.endswith('week'):
    #         ml = re.findall(weekday_rgx, spec)
    #         if ml:
    #             tmp = self._next_weekday(ml[0])
    #             rval = tmp + 7 * _DAY
    #         elif 'this week' in spec:
    #             x = numberize.scan(spec)
    #             nums = [val for val in x if isinstance(val, numbers.Number)]
    #             if 'day' in spec:
    #                 rval = self._week_floor() + (nums[0] - 1) * _DAY
    #         else:
    #             rval = None
    #     return rval

    # -------------------------------------------------------------------------
    # def _interpret(self, base, pieces):
    #     """
    #     Figure out whether the report the beginning or end of a period
    #     ['end', 'of', 'last week']
    #     ['end', 'of', 'the week']
    #     ['beginning', 'of', 'next week']
    #     ['week', 'after', 'next']
    #     ['week', 'before', 'last']
    #     ['beginning', 'of', 'this week']
    #     """
    #     tu = time_units()
    #     rval = None
    #     if 'beginning' in pieces[0]:
    #         rval = base
    #     elif 'end' in pieces[0]:
    #         unit = tu.find_unit(pieces[-1])
    #         rval = base + tu.magnitude(unit) - 1
    #     else:
    #         rval = base
    #     return rval

    # -------------------------------------------------------------------------
    # def _week_ago(self, ref=None, update=False, spec=None):
    #     """
    #     Compute the epoch time of a one week ago
    #     """
    #     ref = ref or self.moment or time.time()
    #     result = numberize.scan(self.spec)
    #     if isinstance(result[0], numbers.Number):
    #         mult = result[0]
    #     else:
    #         mult = 1
    #     ref -= mult * 7 * _DAY
    #     if update:
    #         self.moment = ref
    #     return ref

    # -------------------------------------------------------------------------
    # def _end_of_day(self, wday_name=None, ref=None, update=False):
    #     """
    #     Compute the end of the indicated day
    #
    #     *wday_name* - The name of the target day
    #
    #     If wday_name is specified, we assume 'next'. However, if wday_name
    #     matches the weekday of the CSM, the calculation
    #     applies to the CSM.
    #
    #     Example:
    #         >>> import nldt
    #         >>> foo = nldt.moment()
    #         >>> foo.end_of_day()
    #         1481345999
    #     """
    #     point = ref or self.moment or time.time()
    #     if wday_name:
    #         now = time.localtime(point)
    #         wday_num = _WEEKDAYS[wday_name]
    #         diff = (7 + wday_num - now.tm_wday) % 7
    #     else:
    #         diff = 0
    #     point += diff * _DAY
    #     target = self._day_ceiling(point, update=update)
    #     if update:
    #         self.moment = target
    #     return target

    # -------------------------------------------------------------------------
    # def _end_of_week(self, ref=None, update=False):
    #     """
    #     Compute the end of the week based on CSM
    #     """
    #     ref = ref or self.moment or time.time()
    #     rval = self._end_of_day('sun', ref=ref, update=update)
    #     return rval

    # -------------------------------------------------------------------------
    # def _end_of_month(self, ref=None, update=False):
    #     """
    #     Compute the end of the month.
    #     """
    #     ref = ref or self.moment or time.time()
    #     tm = time.localtime(ref)
    #     maxday = month_days(tm.tm_mon)
    #     rval = time.mktime((tm.tm_year, tm.tm_mon, maxday,
    #                         23, 59, 59,
    #                         0, 0, -1))
    #     if update:
    #         self.moment = rval
    #     return rval

    # -------------------------------------------------------------------------
    # def _end_of_year(self, ref=None, update=False):
    #     """
    #     Compute the end of the year.
    #     """
    #     ref = ref or self.moment or time.time()
    #     tm = time.localtime(ref)
    #     rval = time.mktime((tm.tm_year, 12, 31, 23, 59, 59, 0, 0, -1))
    #     if update:
    #         self.moment = rval
    #     return rval

    # -------------------------------------------------------------------------
    # def _first_week_in_MONTH(self, ref=None, update=False, spec=None):
    #     """
    #     Given MONTH
    #     """
    #     for mname in month_names():
    #         if mname.lower()[0:3] in self.spec.lower():
    #             month = month_index(mname)
    #             break
    #     tmp = moment()
    #     year = tmp('%Y')
    #     target = moment('{}-{}-07'.format(year, month))
    #     while target('%a').lower() != 'mon':
    #         target.parse('yesterday')
    #     rval = target.epoch()
    #     return rval

    # -------------------------------------------------------------------------
    # def _this_week(self, ref=None, update=False, spec=None):
    #     """
    #     Compute and return the epoch time of the beginning of the current
    #     week
    #     """
    #     ref = self._last_weekday('mon')
    #     return ref

    # -------------------------------------------------------------------------
    # def _last_week(self, ref=None, update=False, spec=None):
    #     """
    #     Compute the epoch time of the beginning of last week
    #     """
    #     ref = ref or self.moment or time.time()
    #     rtm = time.localtime(ref)
    #     if 0 < rtm.tm_wday:
    #         ref -= rtm.tm_wday * _DAY
    #     ref = self._day_floor(ref)
    #     ref -= 7 * _DAY
    #     if spec and spec != 'last week':
    #         nums = [x for x in numberize.scan(spec)
    #                 if isinstance(x, numbers.Number)]
    #         if 'day' in spec:
    #             ref += (nums[0] - 1) * _DAY
    #     if update:
    #         self.moment = ref
    #     return ref

    # -------------------------------------------------------------------------
    # def _last_weekday(self, wday_name, ref=None, update=False):
    #     """
    #     Compute the epoch time of the indicated past weekday
    #     """
    #     ref = ref or self.moment or time.time()
    #     wday_num = _WEEKDAYS[wday_name]
    #     now = time.localtime(ref)
    #     diff = (7 + now.tm_wday - wday_num - 1) % 7 + 1
    #     ref -= diff * _DAY
    #     rval = self._day_floor(ref=ref, update=update)
    #     return rval

    # -------------------------------------------------------------------------
    # def _last_year(self, ref=None, update=False):
    #     """
    #     Compute the epoch time of the indicated past year
    #     """
    #     ref = ref or self.moment or time.time()
    #     tm = time.localtime(ref)
    #     lastyear = int(tm.tm_year) - 1
    #     rval = time.mktime((lastyear, 1, 1, 0, 0, 0, 0, 0, -1))
    #     return rval

    # -------------------------------------------------------------------------
    # def _next_weekday(self, wday_name, ref=None, update=False):
    #     """
    #     Compute the epoch time of the indicated future weekday
    #     """
    #     ref = ref or self.moment or time.time()
    #     wday_num = _WEEKDAYS[wday_name]
    #     tm = time.localtime(ref)
    #     diff = (7 + wday_num - tm.tm_wday - 1) % 7 + 1
    #     rval = self._day_floor(ref + diff * _DAY, update=update)
    #     return rval

    # -------------------------------------------------------------------------
    # def _next_year(self, ref=None, update=False):
    #     """
    #     Compute the epoch time of the indicated future year
    #     """
    #     tm = time.localtime(ref)
    #     nextyear = tm.tm_year + 1
    #     rval = time.mktime((nextyear, 1, 1, 0, 0, 0, 0, 0, -1))
    #     return rval

    # -------------------------------------------------------------------------
    # def _end_of_last_week(self, ref=None, update=False, spec=None):
    #     """
    #     Return the moment that ends last week
    #     """
    #     ref = ref or self.moment or time.time()
    #     ref -= _WEEK
    #     ref = self._end_of_day(wday_name='sun', ref=ref)
    #     if update:
    #         self.moment = ref
    #     return ref

    # -------------------------------------------------------------------------
    # def _start_of_next_week(self, ref=None, update=False, spec=None):
    #     """
    #     Return the moment that begins next week
    #     """
    #     ref = ref or self.moment or time.time()
    #     rval = self._end_of_day('mon', ref)
    #     rval = self._day_floor(rval)
    #     if update:
    #         self.moment = rval
    #     return rval

    # -------------------------------------------------------------------------
    # def _week_after_next(self, ref=None, update=False, spec=None):
    #     """
    #     Compute and return epoch time of a week from the next Monday
    #     """
    #     ref = ref or self.moment or time.time()
    #     ref = self._end_of_day('sun', ref=ref)
    #     ref += 7 * _DAY + 1
    #     if update:
    #         self.moment = ref
    #     return ref

    # -------------------------------------------------------------------------
    # def _week_before_last(self, ref=None, update=False, spec=None):
    #     """
    #     Compute and return epoch time of last week's predecessor
    #     """
    #     ref = ref or self.moment or time.time()
    #     ref = self._last_week(ref)
    #     ref = self._last_week(ref)
    #     if update:
    #         self.moment = ref
    #     return ref

    # -------------------------------------------------------------------------
    # def _week_from_now(self, ref=None, update=False, spec=None):
    #     """
    #     Compute a future date based on self.spec
    #     """
    #     ref = ref or self.moment or time.time()
    #     result = numberize.scan(self.spec)
    #     if isinstance(result[0], numbers.Number):
    #         mult = result[0]
    #     else:
    #         mult = 1
    #     ref += int(mult * _WEEK)
    #     if update:
    #         self.moment = ref
    #     return ref

    # -------------------------------------------------------------------------
    # def _tomorrow(self, ref=None, update=False, spec=None):
    #     """
    #     Compute and return epoch time of tomorrow based on ref, self.moment,
    #     or time.time()
    #
    #     Example:
    #         >>> import nldt
    #         >>> a = nldt.moment('2000-12-31')
    #         >>> b = nldt.moment(a._tomorrow())
    #         >>> b()
    #         '2001-01-01'
    #     """
    #     ref = ref or self.moment or time.time()
    #     rval = self._day_floor(ref + _DAY)
    #     if update:
    #         self.moment = rval
    #     return rval

    # -------------------------------------------------------------------------
    # def _yesterday(self, ref=None, update=False, spec=None):
    #     """
    #     Return a moment object based on CSM's yesterday
    #
    #     Example:
    #         >>> import nldt
    #         >>> a = ndlt.moment('2001-11-30')
    #         >>> b = a.yesterday()
    #         >>> b()
    #         '2001-11-29'
    #     """
    #     ref = ref or self.moment or time.time()
    #     rval = self._day_floor(ref - _DAY)
    #     if update:
    #         self.moment = rval
    #     return rval

    # -------------------------------------------------------------------------
    # def _day_ceiling(self, ref=None, update=False):
    #     """
    #     Compute and return the max epoch in the current day
    #     """
    #     ref = ref or self.moment or time.time()
    #
    #     rtm = time.localtime(ref)
    #     delta = 24 * 3600
    #     delta -= rtm.tm_hour * 3600
    #     delta -= rtm.tm_min * 60
    #     delta -= rtm.tm_sec
    #     ref += delta - 1
    #
    #     # tmp = tmp + time.timezone - (tmp % _DAY) + _DAY - 1
    #     if update:
    #         self.moment = ref
    #     return ref

    # -------------------------------------------------------------------------
    # def _week_floor(self, ref=None, update=False):
    #     """
    #     Compute and return the min epoch in the current week
    #     """
    #     ref = ref or self.moment or time.time()
    #     ref_tm = time.localtime(ref)
    #
    #     flr = ref
    #     flr -= ref_tm.tm_wday * _DAY
    #     flr -= ref_tm.tm_hour * 3600
    #     flr -= ref_tm.tm_min * 60
    #     flr -= ref_tm.tm_sec
    #
    #     if update:
    #         self.moment = flr
    #     return flr

    # -------------------------------------------------------------------------
    # def _day_floor(self, ref=None, update=False):
    #     """
    #     Compute and return the min epoch in the current day
    #     """
    #     ref = ref or self.moment or time.time()
    #     ref_tm = time.localtime(ref)
    #
    #     flr = ref
    #     flr -= ref_tm.tm_hour * 3600
    #     flr -= ref_tm.tm_min * 60
    #     flr -= ref_tm.tm_sec
    #
    #     if update:
    #         self.moment = flr
    #     return flr

    # -------------------------------------------------------------------------
    # def timezone(self):
    #     """
    #     Return the timezone based on current CSM
    #
    #     Example:
    #         >>> a = nldt.moment('2004-06-03')
    #         >>> a.timezone()
    #         'EDT'
    #         >>> b = nldt.moment('2005-12-15')
    #         >>> b.timezone()
    #         'EST'
    #     """
    #     lt = time.localtime(self.moment)
    #     return time.tzname[lt.tm_isdst]
    # -------------------------------------------------------------------------
    # def dst(self, timzone=None):
    #     """
    #     Return True or False - whether DST is in force at the CSM
    #
    #     !@! The CSM should be a UTC. To know whether DST is in force, we need
    #     a timezone. The local timezone will be used unless another is
    #     specified
    #
    #     Examples:
    #         >>> import nldt
    #         >>> q = nldt.moment('1962.0317')
    #         >>> q.dst()
    #         False
    #         >>> q.parse('1962.0430')
    #         >>> q.dst()
    #         True
    #     """
    #     tm = time.localtime(self.moment)
    #     return tm.tm_isdst == 1


# -----------------------------------------------------------------------------
class moment(object):
    """
    Objects of this class represent a point in time. The moment is stored in
    UTC.
    """
    formats = ['%y-%m-%d',
               '%y-%m-%d %H',
               '%y-%m-%d %H:%M',
               '%y-%m-%d %H:%M:%S',

               '%Y-%m-%d',
               '%Y-%m-%d %H',
               '%Y-%m-%d %H:%M',
               '%Y-%m-%d %H:%M:%S',

               "%Y.%m%d",
               "%Y.%m%d %H",
               "%Y.%m%d %H:%M",
               "%Y.%m%d %H:%M:%S",

               "%Y-%m-%d",
               "%Y-%m-%d %H",
               "%Y-%m-%d %H:%M",
               "%Y-%m-%d %H:%M:%S",

               "%b %d %Y",
               "%b %d %Y %H",
               "%b %d %Y %H:%M",
               "%b %d %Y %H:%M:%S",

               "%b %d, %Y",
               "%b %d, %Y %H",
               "%b %d, %Y %H:%M",
               "%b %d, %Y %H:%M:%S",

               "%d %b %Y %H:%M:%S",
               "%d %b %Y %H:%M",
               "%d %b %Y %H",
               "%d %b %Y",

               "%d %b, %Y %H:%M:%S",
               "%d %b, %Y %H:%M",
               "%d %b, %Y %H",
               "%d %b, %Y",

               "%B %d %Y %H:%M:%S",
               "%B %d %Y %H:%M",
               "%B %d %Y %H",
               "%B %d %Y",

               "%B %d, %Y %H:%M:%S",
               "%B %d, %Y %H:%M",
               "%B %d, %Y %H",
               "%B %d, %Y",

               "%d %B %Y %H:%M:%S",
               "%d %B %Y %H:%M",
               "%d %B %Y %H",
               "%d %B %Y",

               "%d %B, %Y %H:%M:%S",
               "%d %B, %Y %H:%M",
               "%d %B, %Y %H",
               "%d %B, %Y",
               ]

    # -------------------------------------------------------------------------
    def __init__(self, *args):
        """
        Construct a moment object

        *args*:
            empty: object represents current time at instantiation
            one element: may be a date/time spec matching one of the formats in
                self.formats or a natural language expression describing the
                time of interest (see Examples).
            two elements: args[0] is a date/time spec, args[1] is a format
                describing args[0]

        Examples:
            >>> import nldt
            # current time
            >>> now = nldt.moment()
            >>> now()
            '2016-12-04'
            # listed format
            >>> new_year_day = nldt.moment('2001-01-01')
            >>> new_year_day()
            '2001-01-01'
            # natural language
            >>> yesterday = nldt.moment('yesterday')
            >>> yesterday()
            '2016-12-03'
            >>> nw = nldt.moment('next week')
            >>> nw()
            '2016-12-05'
            # specified format
            >>> then = nldt.moment('Dec 29 2016', '%b %m %Y')
            >>> then()
            '2016-12-29'
        """
        self.moment = None
        if len(args) < 1:
            self.moment = int(time.time())
        elif len(args) < 2:
            if isinstance(args[0], numbers.Number):
                self.moment = int(args[0])
            elif isinstance(args[0], time.struct_time):
                self.moment = timegm(args[0])
            elif isinstance(args[0], tuple):
                if len(args[0]) < 6 or 9 < len(args[0]):
                    raise ValueError('need at least 6 values, no more than 9')
                self.moment = timegm(args[0])
            elif isinstance(args[0], str):
                self.moment = self._guess_format(args[0])
            if self.moment is None:
                msg = "\n".join(["Valid ways of calling nldt.moment():",
                                 "    nldt.moment()",
                                 "    nldt.moment(<epoch-seconds>)",
                                 "    nldt.moment('YYYY-mm-dd')",
                                 "    nldt.moment(<date-str>[, <format>])"])
                raise(ValueError(msg))
        else:
            tm = time.strptime(args[0], args[1])
            self.moment = int(timegm(tm))

    # -------------------------------------------------------------------------
    def __call__(self, format=None, tz=None):
        """
        Return a string representing the date of the CSM

        *format*: Optional string indicating the desired output format.

        Examples:
            >>> import nldt
            >>> a = nldt.moment()
            # No arguments, default format (ISO)
            >>> a()
            '2016-12-04'

            # *format* specified
            >>> a('%Y.%m%d %H:%M:%S')
            '2016.1204 07:16:20'
        """
        format = format or "%Y-%m-%d"
        tz = tz or 'UTC'
        if tz == 'local':
            tm = time.localtime(self.moment)
        elif tz == 'UTC':
            tm = time.gmtime(self.moment)
        else:
            zone = pytz.timezone(tz)
            dt = datetime.fromtimestamp(self.moment)
            offset = zone.utcoffset(dt).total_seconds()
            tm = time.gmtime(self.moment + offset)
            format = format.replace('%Z', zone.tzname(dt))
            format = format.replace('%z', hhmm(offset))
        rval = time.strftime(format, tm)
        return rval

    # -------------------------------------------------------------------------
    def __eq__(self, other):
        """
        Return True or False - whether two moment objects are equal
        implicit)

        *other*: a second moment object to be compared to self

        Examples:
            >>> import nldt

            # instantiated seconds apart, a and b will not be equal
            >>> a = nldt.moment()
            >>> b = nldt.moment()
            >>> a == b
            False

            # however, once they are both advanced to the beginning of
            # tomorrow, so the both record the beginning of the day at
            # midnight, they will be equal
            >>> a.parse('tomorrow')
            >>> b.parse('tomorrow')
            >>> a == b
            True
        """
        return self.moment == other.moment

    # -------------------------------------------------------------------------
    def __repr__(self):
        """
        Return a string that will regenerate this object if passed to eval()

        Examples:
            >>> import nldt
            >>> c = nldt.moment()
            >>> assert eval(repr(c)) == c
            True
            >>> print repr(c)
            nldt.moment(1481000400)
        """
        rval = "nldt.moment({:d})".format(int(self.moment))
        return rval

    # -------------------------------------------------------------------------
    def __str__(self):
        """
        Return a human-readable representation of this object

        Examples:
            >>> import nldt
            >>> c = nldt.moment()
            >>> print(c)
            2016-12-04 07:31:08
        """
        return time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(self.moment))

    # -------------------------------------------------------------------------
    def epoch(self):
        """
        Return the CSM as an int epoch time

        Examples:
            >>> import nldt
            >>> q = nldt.moment()
            >>> q.epoch()
            1480855032
        """
        return int(self.moment)

    # -------------------------------------------------------------------------
    def gmtime(self):
        """
        Return the UTC tm structure for the CSM

        examples:
            >>> import nldt
            >>> q = nldt.moment()
            >>> q.gmtime()
            time.struct_time(tm_year=2016, tm_mon=12, tm_mday=4, tm_hour=7,
            tm_min=37, tm_sec=12, tm_wday=6, tm_yday=339, tm_isdst=0)
        """
        return time.gmtime(self.moment)

    # -------------------------------------------------------------------------
    def localtime(self):
        """
        Return the tm structure for the CSM

        examples:
            >>> import nldt
            >>> q = nldt.moment()
            >>> q.localtime()
            time.struct_time(tm_year=2016, tm_mon=12, tm_mday=4, tm_hour=7,
            tm_min=37, tm_sec=12, tm_wday=6, tm_yday=339, tm_isdst=0)
        """
        return time.localtime(self.moment)

    # -------------------------------------------------------------------------
    def ceiling(self, unit):
        """
        Compute the ceiling of *unit* (second, minute, hour, day, etc.) from
        *self*.epoch()
        """
        tm = time.gmtime(self.epoch())
        if unit == 'second':
            ceil = self.epoch()
        elif unit == 'minute':
            ceil = timegm((tm.tm_year, tm.tm_mon, tm.tm_mday,
                           tm.tm_hour, tm.tm_min, 59, 0, 0, 0))
        elif unit == 'hour':
            ceil = timegm((tm.tm_year, tm.tm_mon, tm.tm_mday,
                           tm.tm_hour, 59, 59, 0, 0, 0))
        elif unit == 'day':
            ceil = timegm((tm.tm_year, tm.tm_mon, tm.tm_mday,
                           23, 59, 59, 0, 0, 0))
        elif unit == 'week':
            ceil = timegm((tm.tm_year, tm.tm_mon, tm.tm_mday + (6-tm.tm_wday),
                           23, 59, 59, 0, 0, 0))
        elif unit == 'month':
            maxday = month.days(year=tm.tm_year, month=tm.tm_mon)
            ceil = timegm((tm.tm_year, tm.tm_mon, maxday,
                           23, 59, 59, 0, 0, 0))
        elif unit == 'year':
            ceil = timegm((tm.tm_year, 12, 31, 23, 59, 59, 0, 0, 0))
        else:
            raise ValueError('unit must be a time unit')
        return moment(ceil)

    # -------------------------------------------------------------------------
    def floor(self, unit):
        """
        Compute the floor of *unit* (second, minute, hour, day, etc.) from
        *self*.epoch()
        """
        epoch = self.epoch()
        if unit == 'second':
            rval = self
        elif unit == 'minute':
            tm = time.gmtime(epoch)
            floor = timegm((tm.tm_year, tm.tm_mon, tm.tm_mday,
                            tm.tm_hour, tm.tm_min, 0, 0, 0, 0))
            rval = moment(floor)
        elif unit == 'hour':
            tm = time.gmtime(epoch)
            floor = timegm((tm.tm_year, tm.tm_mon, tm.tm_mday, tm.tm_hour,
                            0, 0, 0, 0, 0))
            rval = moment(floor)
        elif unit == 'day':
            tm = time.gmtime(epoch)
            floor = timegm((tm.tm_year, tm.tm_mon, tm.tm_mday, 0, 0, 0,
                            0, 0, 0))
            rval = moment(floor)
        elif unit == 'week':
            tm = time.gmtime(epoch)
            floor = timegm((tm.tm_year, tm.tm_mon, tm.tm_mday - tm.tm_wday,
                            0, 0, 0, 0, 0, 0))
            rval = moment(floor)
        elif unit == 'month':
            tm = time.gmtime(epoch)
            nflr = timegm((tm.tm_year, tm.tm_mon, 1, 0, 0, 0, 0, 0, 0))
            rval = moment(nflr)
        elif unit == 'year':
            tm = time.gmtime(epoch)
            nflr = timegm((tm.tm_year, 1, 1, 0, 0, 0, 0, 0, 0))
            rval = moment(nflr)
        else:
            raise ValueError('unit must be a time unit')
        return rval

    # -------------------------------------------------------------------------
    def week_floor(self):
        """
        Find the beginning of the week in which *self*.moment occurs and return
        a new moment object that stores that point in time.
        """
        tm = time.gmtime(self.moment)
        then = self.epoch()
        then -= tm.tm_wday * _DAY
        then -= tm.tm_hour * _HOUR
        then -= tm.tm_min * _MINUTE
        then -= tm.tm_sec
        return moment(then)

    # -------------------------------------------------------------------------
    def month_ceiling(self):
        """
        Find the end of the month that contains *self*.moment
        """
        tm = time.gmtime(self.epoch())
        nflr_tm = (tm.tm_year, tm.tm_mon + 1, 1, 0, 0, 0, 0, 0, 0)
        nflr = timegm(nflr_tm)
        nflr -= nflr % _DAY
        return moment(nflr - 1)

    # -------------------------------------------------------------------------
    def month_floor(self):
        """
        Find the beginning of the month that contains *self*.moment
        """
        tm = time.gmtime(self.epoch())
        flr_tm = (tm.tm_year, tm.tm_mon, 1, 0, 0, 0, 0, 0, 0)
        flr = timegm(flr_tm)
        return moment(flr)

    # -------------------------------------------------------------------------
    def _guess_format(self, spec):
        """
        Try each of the parse formats in the list until one works or the list
        is exhausted
        """
        tm = None
        for fmt in self.formats:
            try:
                tm = time.strptime(spec, fmt)
                break
            except ValueError:
                pass

        if tm:
            return timegm(tm)
        else:
            return None
