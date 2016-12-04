"""
Natural Language Date and Time package

This module provides a simple interfaace to Python's time and date processing
machinery.
"""
import numbers
import pdb
import re
import time


DAY = 24*3600      # !@! should be private
WEEK = 7 * DAY     # !@! should be private


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
_WEEKDAYS = {'mon': 0, 0: 'mon',
             'tue': 1, 1: 'tue',
             'wed': 2, 2: 'wed',
             'thu': 3, 3: 'thu',
             'fri': 4, 4: 'fri',
             'sat': 5, 5: 'sat',
             'sun': 6, 6: 'sun'}


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
class moment(object):
    """
    This class describes objects representing a point in time

    Documentation for the methods mentions the CSM, the currently stored
    moment.
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
    nldict = {'end of last week': 'end_of_last_week',
              'tomorrow': '_tomorrow',
              }

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
                self.moment = self.parse_return(args[0])
            elif isinstance(args[0], numbers.Number):
                self.moment = int(args[0])
        else:
            self.moment = int(time.mktime(time.strptime(args[0], args[1])))

    # -------------------------------------------------------------------------
    def __call__(self, format=None):
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
        rval = time.strftime(format, time.localtime(self.moment))
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
        self.moment = self.parse_return(spec)

    # -------------------------------------------------------------------------
    def _day_ceiling(self, ref=None, update=False):
        """
        Compute and return the max epoch in the current day
        """
        tmp = ref or self.moment or time.time()
        tmp = tmp - (tmp % DAY) + time.timezone + DAY - 1
        if update:
            self.moment = tmp
        return tmp

    # -------------------------------------------------------------------------
    def _end_of_day(self, ref=None, wday_name=None, update=False):
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
        point += diff * DAY
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
        rval = self._end_of_day(ref=ref, wday_name='sun', update=update)
        return rval

    # -------------------------------------------------------------------------
    def _end_of_month(self, ref=None, update=False):
        """
        Compute the end of the month.
        """
        ref = ref or self.moment or time.time()
        rval = None
        return rval

    # -------------------------------------------------------------------------
    def end_of_year(self):
        """
        Compute the end of the year.
        !@! needs example
        """
        rval = None
        return rval

    # -------------------------------------------------------------------------
    def last_weekday(self, wday_name):
        """
        Compute the epoch time of the indicated future weekday
        !@! needs example
        """
        wday_num = _WEEKDAYS[wday_name]
        ref = self.moment or time.time()
        now = time.localtime(ref)
        diff = (7 + now.tm_wday - wday_num - 1) % 7 + 1
        rval = ref - diff * DAY
        return rval

    # -------------------------------------------------------------------------
    def last_year(self):
        """
        Compute the epoch time of the indicated past year
        !@! needs example
        """
        thisyear = time.strftime("%Y")
        lastyear = int(thisyear) - 1
        lsyr_s = "{}-01-01".format(lastyear)
        tm = time.strptime(lsyr_s, "%Y-%m-%d")
        rval = time.mktime(tm)
        return rval

    # -------------------------------------------------------------------------
    def next_weekday(self, wday_name):
        """
        Compute the epoch time of the indicated future weekday
        !@! needs example
        """
        ref = self.moment or time.time()
        wday_num = _WEEKDAYS[wday_name]
        now = time.localtime()
        diff = (7 + wday_num - now.tm_wday - 1) % 7 + 1
        rval = ref + diff * DAY
        return rval

    # -------------------------------------------------------------------------
    def next_year(self):
        """
        Compute the epoch time of the indicated future year
        !@! needs example
        """
        thisyear = time.strftime("%Y")
        nextyear = int(thisyear) + 1
        nxyr_s = "{}-01-01".format(nextyear)
        tm = time.strptime(nxyr_s, "%Y-%m-%d")
        rval = time.mktime(tm)
        return rval

    # -------------------------------------------------------------------------
    def guess_format(self, spec):
        """
        !@! needs example and description
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
    def parse_return(self, spec):
        """
        Figure out what spec means -- the heavy lift of parsing

        spec - A date/time specification

        Example:
            foo = when.when()
            foo.parse('2013.0630')
            foo.parse('next friday at 5')

        internal
        """
        rval = self.guess_format(spec)
        if rval is not None:
            return rval

        if spec in self.nldict:
            func = getattr(self, self.nldict[spec])
            return func()

        weekday_rgx = '(mon|tue|wed|thu|fri|sat|sun)'
        if spec == 'yesterday':
            ref = self.moment or time.time()
            yest = ref - DAY
            rval = yest - yest % (DAY) + time.timezone
        elif 'end of' in spec:
            ml = re.findall(weekday_rgx, spec)
            if ml:
                rval = self.end_of_day(ml[0])
            elif 'last week' in spec:
                now = self.moment or time.time()
                tmp = moment(now - 7 * DAY)
                rval = tmp.end_of_week()
            elif 'week' in spec:
                rval = self.end_of_week()
            elif 'month' in spec:
                rval = self.end_of_month()
            elif 'year' in spec:
                rval = self.end_of_year()
        elif 'next' in spec:
            ml = re.findall(weekday_rgx, spec)
            if ml:
                rval = self.next_weekday(ml[0])
            else:
                if 'week' in spec:
                    rval = self.next_weekday('mon')
                elif 'month' in spec:
                    rval = self.next_month()
                elif 'year' in spec:
                    rval = self.next_year()
        elif 'last' in spec:
            ml = re.findall(weekday_rgx, spec)
            if ml:
                rval = self.last_weekday(ml[0])
            else:
                if 'week' in spec:
                    ref = self.moment or time.time()
                    ref -= 7 * DAY
                    tmp = moment(ref)
                    rval = tmp.last_weekday('mon')
                elif 'month' in spec:
                    rval = self.last_month()
                elif 'year' in spec:
                    rval = self.last_year()
        elif spec.endswith('week'):
            ml = re.findall(weekday_rgx, spec)
            if ml:
                tmp = self.next_weekday(ml[0])
                rval = tmp + 7 * DAY
            else:
                rval = None
        return rval

    # -------------------------------------------------------------------------
    def timezone(self):
        """
        Return the timezone based on current CSM

        Example:
            >>> a = nldt.moment('2004-06-03')
            >>> a.timezone()
            'EDT'
            >>> b = nldt.moment('2005-12-15')
            >>> b.timezone()
            'EST'
        """
        lt = time.localtime(self.moment)
        return time.tzname[lt.tm_isdst]

    # -------------------------------------------------------------------------
    def _tomorrow(self, ref=None):
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
        tmr = ref or self.moment or time.time()
        tmr += DAY
        rval = tmr - (tmr % DAY) + time.timezone
        return rval

    # -------------------------------------------------------------------------
    def tomorrow(self):
        """
        Return a moment object based on CSM's tomorrow

        Example:
            >>> import nldt
            >>> a = ndlt.moment('2001-11-30')
            >>> b = a.tomorrow()
            >>> b()
            '2001-12-01'
        """
        rval = moment(self._tomorrow())
        return rval

    # -------------------------------------------------------------------------
    def yesterday(self):
        """
        Return a moment object based on CSM's yesterday

        Example:
            >>> import nldt
            >>> a = ndlt.moment('2001-11-30')
            >>> b = a.yesterday()
            >>> b()
            '2001-11-29'
        """
        yest = self.moment - DAY
        rval = moment(yest - (yest % DAY) + time.timezone)
        return rval

    # -------------------------------------------------------------------------
    def end_of_last_week(self, update=False):
        """
        Return the moment that ends last week
        """
        ref = self.moment or time.time()
        ref -= WEEK
        ref = self._end_of_day(wday_name='sun', ref=ref)
        if update:
            self.moment = ref
        return ref
