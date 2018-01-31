"""
Natural Language Date and Time package

This module provides a simple natural language interfaace to Python's time and
date processing machinery.
"""
import numberize
import numbers
import re
import time


_DAY = 24*3600
_WEEK = 7 * _DAY


# -----------------------------------------------------------------------------
def dst():
    """
    Return True or False - daylight savings time is in force or not

    Examples:
        >>> import nldt
        >>> nldt.dst()
        False
    """
    now = time.localtime()
    return now.tm_isdst == 1


# -----------------------------------------------------------------------------
def timezone():
    """
    Return the locally configured timezone name

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
def month_days(month):
    """
    Given month name, return the number of days in the month for the current
    year

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
                 if re.search("(^|\s){}(\s|$)".format(unit), text)]
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


# -----------------------------------------------------------------------------
class moment(object):
    """
    Objects of this class represent a point in time.

    csm: currently stored moment
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
            if type(args[0]) == str:
                self.moment = self._parse_return(args[0])
            elif isinstance(args[0], numbers.Number):
                self.moment = int(args[0])
        else:
            self.moment = int(time.mktime(time.strptime(args[0], args[1])))

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
        return time.strftime('%Y-%m-%d %H:%M:%S',
                             time.localtime(self.moment))

    # -------------------------------------------------------------------------
    def dst(self):
        """
        Return True or False - whether DST is in force at the CSM

        Examples:
            >>> import nldt
            >>> q = nldt.moment('1962.0317')
            >>> q.dst()
            False
            >>> q.parse('1962.0430')
            >>> q.dst()
            True
        """
        tm = time.localtime(self.moment)
        return tm.tm_isdst == 1

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
    def parse(self, spec):
        """
        Set the object's value to the date/time indicated by *spec*

        *spec* - A date/time specification in a string, possibly natural
                 language

        Calculations are relative to the CSM (see the example -- after parsing
        '2013.0630', the calculation of 'next friday' is relative to
        2013-06-30, not to the present moment)

        Example:
            >>> import nldt
            >>> foo = nldt.moment()
            >>> foo.parse('next friday')
            >>> foo()
            '2016-12-09'
            >>> foo.parse('2013.0630')
            >>> foo.parse('next friday')
            >>> foo()
            '2013-07-05'
        """
        self.moment = self._parse_return(spec)

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

        if tm is not None:
            return time.mktime(tm)
        else:
            return None

    # -------------------------------------------------------------------------
    def _nl_match(self, spec):
        """
        Look for matches for *spec* in the natural lanugage dictionary

        Example:
            >>> function = self._nl_match('first week in January')
            >>> function
            <bound method '_first_week_in'>
        """
        self.spec = spec
        if spec in self.nldict:
            rval = getattr(self, self.nldict[spec])
            return rval
        for key in self.nldict:
            if key in spec:
                rval = getattr(self, self.nldict[key])
                return rval
        return None

    # -------------------------------------------------------------------------
    nldict = {'end of last week': '_end_of_last_week',
              'last week': '_last_week',
              'first week in': '_first_week_in_MONTH',
              'start of next week': '_start_of_next_week',
              'week from now': '_week_from_now',
              'tomorrow': '_tomorrow',
              'week after next': '_week_after_next',
              'week ago': '_week_ago',
              'week before last': '_week_before_last',
              'week earlier': '_week_ago',
              'week later': '_week_from_now',
              'yesterday': '_yesterday',
              }

    # -------------------------------------------------------------------------
    def _parse_return(self, spec):
        """
        Figure out what spec means -- the heavy lift of parsing

        spec - A date/time specification

        Example:
            foo = when.when()
            foo.parse('2013.0630')
            foo.parse('next friday at 5')

        internal
        """
        rval = self._guess_format(spec)
        if rval is not None:
            return rval

        spec = spec.replace('beginning', 'start')
        spec = spec.replace('weeks', 'week')

        func = self._nl_match(spec)
        if func:
            return func()

        weekday_rgx = '(mon|tue|wed|thu|fri|sat|sun)'
        if spec == 'yesterday':
            ref = self.moment or time.time()
            yest = ref - _DAY
            rval = yest - yest % (_DAY) + time.timezone
        elif 'end of' in spec:
            ml = re.findall(weekday_rgx, spec)
            if ml:
                rval = self.end_of_day(ml[0])
            elif 'last week' in spec:
                now = self.moment or time.time()
                tmp = moment(now - 7 * _DAY)
                rval = tmp._end_of_week()
            elif 'week' in spec:
                rval = self._end_of_week()
            elif 'month' in spec:
                rval = self._end_of_month()
            elif 'year' in spec:
                rval = self._end_of_year()
        elif 'next' in spec:
            ml = re.findall(weekday_rgx, spec)
            if ml:
                rval = self._next_weekday(ml[0])
            else:
                if 'week' in spec:
                    rval = self._next_weekday('mon')
                elif 'month' in spec:
                    rval = self._next_month()
                elif 'year' in spec:
                    rval = self._next_year()
        elif 'last' in spec:
            ml = re.findall(weekday_rgx, spec)
            if ml:
                rval = self._last_weekday(ml[0])
            else:
                if 'week' in spec:
                    tmp = moment(time.time() - 7*_DAY)
                    rval = tmp._last_weekday('mon')
                elif 'month' in spec:
                    rval = self._last_month()
                elif 'year' in spec:
                    rval = self._last_year()
        elif spec.endswith('week'):
            ml = re.findall(weekday_rgx, spec)
            if ml:
                tmp = self._next_weekday(ml[0])
                rval = tmp + 7 * _DAY
            else:
                rval = None
        return rval

    # -------------------------------------------------------------------------
    def _week_ago(self, ref=None, update=False):
        """
        Compute the epoch time of a one week ago
        """
        ref = ref or self.moment or time.time()
        result = numberize.scan(self.spec)
        if isinstance(result[0], numbers.Number):
            mult = result[0]
        else:
            mult = 1
        ref -= mult * 7 * _DAY
        if update:
            self.moment = ref
        return ref

    # -------------------------------------------------------------------------
    def _end_of_day(self, wday_name=None, ref=None, update=False):
        """
        Compute the end of the indicated day

        *wday_name* - The name of the target day

        If wday_name is specified, we assume 'next'. However, if wday_name
        matches the weekday of the CSM, the calculation
        applies to the CSM.

        Example:
            >>> import nldt
            >>> foo = nldt.moment()
            >>> foo.end_of_day()
            1481345999
        """
        point = ref or self.moment or time.time()
        if wday_name:
            now = time.localtime(point)
            wday_num = _WEEKDAYS[wday_name]
            diff = (7 + wday_num - now.tm_wday) % 7
        else:
            diff = 0
        point += diff * _DAY
        target = self._day_ceiling(point, update=update)
        if update:
            self.moment = target
        return target

    # -------------------------------------------------------------------------
    def _end_of_week(self, ref=None, update=False):
        """
        Compute the end of the week based on CSM
        """
        ref = ref or self.moment or time.time()
        rval = self._end_of_day('sun', ref=ref, update=update)
        return rval

    # -------------------------------------------------------------------------
    def _end_of_month(self, ref=None, update=False):
        """
        Compute the end of the month.
        """
        ref = ref or self.moment or time.time()
        tm = time.localtime(ref)
        maxday = month_days(tm.tm_mon)
        rval = time.mktime((tm.tm_year, tm.tm_mon, maxday,
                            23, 59, 59,
                            0, 0, -1))
        if update:
            self.moment = rval
        return rval

    # -------------------------------------------------------------------------
    def _end_of_year(self, ref=None, update=False):
        """
        Compute the end of the year.
        """
        ref = ref or self.moment or time.time()
        tm = time.localtime(ref)
        rval = time.mktime((tm.tm_year, 12, 31, 23, 59, 59, 0, 0, -1))
        if update:
            self.moment = rval
        return rval

    # -------------------------------------------------------------------------
    def _first_week_in_MONTH(self, ref=None, update=False):
        """
        Given MONTH
        """
        for mname in month_names():
            if mname.lower()[0:3] in self.spec.lower():
                month = month_index(mname)
                break
        tmp = moment()
        year = tmp('%Y')
        target = moment('{}-{}-07'.format(year, month))
        while target('%a').lower() != 'mon':
            target.parse('yesterday')
        rval = target.epoch()
        return rval

    # -------------------------------------------------------------------------
    def _last_week(self, ref=None, update=False):
        """
        Compute the epoch time of the beginning of last week
        """
        ref = ref or self.moment or time.time()
        rtm = time.localtime(ref)
        if 0 < rtm.tm_wday:
            ref -= rtm.tm_wday * _DAY
        ref = self._day_floor(ref)
        ref -= 7 * _DAY
        if update:
            self.moment = ref
        return ref

    # -------------------------------------------------------------------------
    def _last_weekday(self, wday_name, ref=None, update=False):
        """
        Compute the epoch time of the indicated past weekday
        """
        ref = ref or self.moment or time.time()
        wday_num = _WEEKDAYS[wday_name]
        now = time.localtime(ref)
        diff = (7 + now.tm_wday - wday_num - 1) % 7 + 1
        ref -= diff * _DAY
        rval = self._day_floor(ref=ref, update=update)
        return rval

    # -------------------------------------------------------------------------
    def _last_year(self, ref=None, update=False):
        """
        Compute the epoch time of the indicated past year
        """
        ref = ref or self.moment or time.time()
        tm = time.localtime(ref)
        lastyear = int(tm.tm_year) - 1
        rval = time.mktime((lastyear, 1, 1, 0, 0, 0, 0, 0, -1))
        return rval

    # -------------------------------------------------------------------------
    def _next_weekday(self, wday_name, ref=None, update=False):
        """
        Compute the epoch time of the indicated future weekday
        """
        ref = ref or self.moment or time.time()
        wday_num = _WEEKDAYS[wday_name]
        tm = time.localtime(ref)
        diff = (7 + wday_num - tm.tm_wday - 1) % 7 + 1
        rval = self._day_floor(ref + diff * _DAY, update=update)
        return rval

    # -------------------------------------------------------------------------
    def _next_year(self, ref=None, update=False):
        """
        Compute the epoch time of the indicated future year
        """
        tm = time.localtime(ref)
        nextyear = tm.tm_year + 1
        rval = time.mktime((nextyear, 1, 1, 0, 0, 0, 0, 0, -1))
        return rval

    # -------------------------------------------------------------------------
    def _end_of_last_week(self, ref=None, update=False):
        """
        Return the moment that ends last week
        """
        ref = ref or self.moment or time.time()
        ref -= _WEEK
        ref = self._end_of_day(wday_name='sun', ref=ref)
        if update:
            self.moment = ref
        return ref

    # -------------------------------------------------------------------------
    def _start_of_next_week(self, ref=None, update=False):
        """
        Return the moment that begins next week
        """
        ref = ref or self.moment or time.time()
        rval = self._end_of_day('mon', ref)
        rval = self._day_floor(rval)
        if update:
            self.moment = rval
        return rval

    # -------------------------------------------------------------------------
    def _week_after_next(self, ref=None, update=False):
        """
        Compute and return epoch time of a week from the next Monday
        """
        ref = ref or self.moment or time.time()
        ref = self._end_of_day('sun', ref=ref)
        ref += 7 * _DAY + 1
        if update:
            self.moment = ref
        return ref

    # -------------------------------------------------------------------------
    def _week_before_last(self, ref=None, update=False):
        """
        Compute and return epoch time of last week's predecessor
        """
        ref = ref or self.moment or time.time()
        ref = self._last_week(ref)
        ref = self._last_week(ref)
        if update:
            self.moment = ref
        return ref

    # -------------------------------------------------------------------------
    def _week_from_now(self, ref=None, update=False):
        """
        Compute a future date based on self.spec
        """
        ref = ref or self.moment or time.time()
        result = numberize.scan(self.spec)
        if isinstance(result[0], numbers.Number):
            mult = result[0]
        else:
            mult = 1
        ref += int(mult * _WEEK)
        if update:
            self.moment = ref
        return ref

    # -------------------------------------------------------------------------
    def _tomorrow(self, ref=None, update=False):
        """
        Compute and return epoch time of tomorrow based on ref, self.moment, or
        time.time()

        Example:
            >>> import nldt
            >>> a = nldt.moment('2000-12-31')
            >>> b = nldt.moment(a._tomorrow())
            >>> b()
            '2001-01-01'
        """
        ref = ref or self.moment or time.time()
        rval = self._day_floor(ref + _DAY)
        if update:
            self.moment = rval
        return rval

    # -------------------------------------------------------------------------
    def _yesterday(self, ref=None, update=False):
        """
        Return a moment object based on CSM's yesterday

        Example:
            >>> import nldt
            >>> a = ndlt.moment('2001-11-30')
            >>> b = a.yesterday()
            >>> b()
            '2001-11-29'
        """
        ref = ref or self.moment or time.time()
        rval = self._day_floor(ref - _DAY)
        if update:
            self.moment = rval
        return rval

    # -------------------------------------------------------------------------
    def _day_ceiling(self, ref=None, update=False):
        """
        Compute and return the max epoch in the current day
        """
        ref = ref or self.moment or time.time()

        rtm = time.localtime(ref)
        delta = 24 * 3600
        delta -= rtm.tm_hour * 3600
        delta -= rtm.tm_min * 60
        delta -= rtm.tm_sec
        ref += delta - 1

        # tmp = tmp + time.timezone - (tmp % _DAY) + _DAY - 1
        if update:
            self.moment = ref
        return ref

    # -------------------------------------------------------------------------
    def _day_floor(self, ref=None, update=False):
        """
        Compute and return the min epoch in the current day
        """
        ref = ref or self.moment or time.time()
        ref_tm = time.localtime(ref)

        flr = ref
        flr -= ref_tm.tm_hour * 3600
        flr -= ref_tm.tm_min * 60
        flr -= ref_tm.tm_sec

        if update:
            self.moment = flr
        return flr


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
