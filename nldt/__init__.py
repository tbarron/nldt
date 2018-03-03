"""
nldt - Natural Language Date/Time support
Copyright (c) 2017 - <the end of time>  Tom Barron
See file LICENSING for details

This file contains code for testing nldt functionality.
-------------------------------------------------------------------------------

Natural Language Date and Time package

This module provides a simple natural language interfaace to Python's time and
date processing machinery.

NLDT Rules

 * The basic time representation is an epoch, which is a 64 bit int
   representing the number of seconds since Thu Jan 1 00:00:00 1970 UTC. Epoch
   values always reflect UTC (not local) time.

 * NLDT stores epoch values in objects of moment class, which provides a number
   of useful methods.

 * The NLDT classes month, week, and time_units depend on functionality
   provided by Python.

 * The NLDT classes moment and duration depend on month, week, time_units, and
   functionality provided by Python.

 * Actual natural language parsing is provided in a layer above moment and
   duration. Nothing in a lower layer should ever depend on something in a
   higher layer. Here's the 'layer cake':


       Layer  Functionality
       ----------------------------------------------------------------
        4     natural language command line interface
       ----------------------------------------------------------------
        3     natural language parsing ('tommorrow', 'yesterday', etc.)
       ----------------------------------------------------------------
        2     moment, duration
       ----------------------------------------------------------------
        1     month, week, time_units
       ----------------------------------------------------------------
        0     Python
       ----------------------------------------------------------------

  * Calculations are carried out in UTC. Dates and times are only converted to
    local time when being delivered to the consumer, if desired.

We import and use calendar.timegm because it provides something the time module
is missing. Specifically, the time provides:

  * gmtime (convert UTC epoch to UTC tm struct),
  * localtime (convert UTC epoch to local time tm struct), and
  * mktime (convert local time tm struct to UTC epoch),

but it does not provide a way to get from a UTC tm struct to UTC epoch.

If we apply time.mktime to a UTC tm struct, the resulting epoch is adjusted by
the UTC offset. Since local time's UTC offset may change from one part of the
year to another as DST goes on and off, using mktime and then adjusting
backward is problematic and confusing.

The better solution is to import and use calendar.timegm() because it provides
the desired functionality, converting a UTC tm struct to the corresponding UTC
epoch.
"""
import calendar
import contextlib
from datetime import datetime
from tzlocal import get_localzone
import inspect
from nldt import numberize
import numbers
import os
import pytz
import re
from nldt.text import txt
import time
from nldt import verinfo


# -----------------------------------------------------------------------------
class duration(object):
    """
    This class represents a time interval by storing the number of seconds in
    the interval.
    """
    def __init__(self, start=None, end=None,
                 years=None, weeks=None, days=None, hours=None, minutes=None,
                 seconds=None):
        """
        If *start* or *end* are present, both must be, and none of the other
        arguments are allowed. Each can be in any of the following formats: 1)
        an epoch, 2) a tm struct, 3) a moment, or 4) a date/time string in a
        format moment recognizes, and they don't have to be in the same format.
        You could pass in *start* as a moment and *end* as a tm struct, for
        example.

        If *start* and *end* are both absent, any combination of *years*,
        *weeks*, *days*, *hours*, *minutes*, and *seconds* can be used.
        """
        if start or end:
            # build duration from the difference between end and start
            if not start or not end:
                raise InitError(txt['mctor_001'])
            start = self._resolve_value(start)
            end = self._resolve_value(end)
            self.seconds = end.epoch() - start.epoch()
        else:
            # build duration from years, weeks, days, hours, minutes, seconds
            tsecs = 0
            tu = time_units()
            if seconds:
                tsecs += seconds
            if minutes:
                tsecs += tu.magnitude('minute') * minutes
            if hours:
                tsecs += tu.magnitude('hour') * hours
            if days:
                tsecs += tu.magnitude('day') * days
            if weeks:
                tsecs += tu.magnitude('week') * weeks
            if years:
                tsecs += tu.magnitude('year') * years
            self.seconds = tsecs

    # -------------------------------------------------------------------------
    def __repr__(self):
        """
        Return an object representation suitable to be processed by eval (class
        duration)
        """
        return "{}.{}(seconds={})".format(self.__module__,
                                          self.__class__.__name__,
                                          self.seconds)

    # -------------------------------------------------------------------------
    def __str__(self):
        """
        Return the objects str suitable human consumption (class duration)
        """
        secs = self.seconds
        days = int(secs / (3600 * 24))
        secs -= days * 3600 * 24
        hours = int(secs / 3600)
        secs -= hours * 3600
        minutes = int(secs / 60)
        secs -= minutes * 60
        return "{:d}.{:02d}:{:02d}:{:02d}".format(days, hours, minutes, secs)

    # -------------------------------------------------------------------------
    def __add__(self, other):
        """
        Add *other* to *self*
         - duration + moment => moment
         - duration + duration => duration
         - duration + number-of-seconds => duration
        (class duration)
        """
        if isinstance(other, duration):
            rval = duration(seconds=self.seconds + other.seconds)
        elif isinstance(other, numbers.Number):
            rval = duration(seconds=self.seconds + other)
        elif isinstance(other, moment):
            rval = moment(other + self.seconds)
        else:
            other = moment(other)
            rval = other + self
        return rval

    # -------------------------------------------------------------------------
    def __call__(self, fmtstr):
        """
        This function reports the stored interval according to fmtstr (class
        duration)
        """
        interval = self._deconstruct()
        result = fmtstr
        sfmt = "{}"
        for foo in ["Y", "d", "H", "M", "S"]:
            result = re.sub("%"+foo, sfmt.format(interval[foo]), result)
            if foo == "d":
                sfmt = "{:02d}"
        return result

    # -------------------------------------------------------------------------
    def __eq__(self, other):
        """
        Assess whether this object is equal to the *other* value (class
        duration)
        """
        if isinstance(other, numbers.Number):
            return self.seconds == other
        elif isinstance(other, duration):
            return self.seconds == other.seconds

    # -------------------------------------------------------------------------
    def __sub__(self, other):
        """
        Subtract *other* from *self*
          - duration - duration => duration
          - duration - number-of-seconds => duration
          - duration - moment => exception
        (class duration)
        """
        if isinstance(other, numbers.Number):
            rval = self.seconds - other
        elif isinstance(other, duration):
            rval = self.seconds - other.seconds
        elif isinstance(other, moment):
            raise TypeError(txt['optypes_01'])
        else:
            raise TypeError(txt['optypes_02'].format(type(self), type(other)))
        return rval

    # -------------------------------------------------------------------------
    def _deconstruct(self):
        """
        Allocate the seconds to a year, day, hour, min, sec dict (class
        duration)
        """
        rval = {}
        secs = self.seconds
        rval["Y"] = int(secs / (365*24*3600))
        secs -= rval["Y"] * 365*24*3600
        rval["d"] = int(secs / (24*3600))
        secs -= rval["d"] * 24*3600
        rval["H"] = int(secs / 3600)
        secs -= rval["H"] * 3600
        rval["M"] = int(secs / 60)
        secs -= rval["M"] * 60
        rval["S"] = int(secs)
        return rval

    # -------------------------------------------------------------------------
    def _resolve_value(self, start_end_value):
        """
        *start_end_value* may be any of the following types:

            1) an epoch number,
            2) a moment,
            3) a string representing an epoch number,
            2) a tm struct,
            3) a tuple (6 to 9 numbers), or
            4) a date/time string in a format moment recognizes,

        and they don't have to be in the same format. (class duration)
        """
        if isinstance(start_end_value, numbers.Number):
            rval = moment(start_end_value)
        elif isinstance(start_end_value, moment):
            rval = start_end_value
        elif isinstance(start_end_value, time.struct_time):
            rval = moment(start_end_value, itz='utc')
        elif isinstance(start_end_value, tuple):
            if len(start_end_value) < 6 or 9 < len(start_end_value):
                raise InitError(txt['invtup'])
            else:
                rval = moment(start_end_value, itz='utc')
        elif isinstance(start_end_value, str):
            rval = moment(start_end_value, itz='utc')
        return rval

    # -------------------------------------------------------------------------
    def dhms(self):
        """
        This method reports a duration as <days>.HH:MM:SS in a string (class
        duration)
        """
        secs = self.seconds
        days = int(secs / (24*3600))
        secs -= days * 24 * 3600
        hours = int(secs / 3600)
        secs -= hours * 3600
        minutes = int(secs / 60)
        secs -= minutes * 60
        rval = "{}.{:02d}:{:02d}:{:02d}".format(days, hours, minutes, secs)
        return rval

    # -------------------------------------------------------------------------
    def sleep(self):
        """
        sleep for the duration period (class duration)
        """
        time.sleep(self.seconds)


# -----------------------------------------------------------------------------
class Indexable(object):
    """
    This class has a _dict dictionary member and a method called indexify that
    will take an argument that may be a number or string and return a numeric
    index for one of the members of _dict. This class is intended as an
    abstract base class for week and month.
    """
    # -------------------------------------------------------------------------
    def __init__(self):
        """
        Don't instantiate this class. It is an abstract base for month and
        week. (class Indexable)
        """
        raise TypeError("This is an abstract base class -- "
                        "don't instantiate it.")

    # -------------------------------------------------------------------------
    def indexify(self, name_or_idx):
        """
        Return an int idx in the range [0, 7) (i.e., between 0 and 6 inclusive)
        or -1. (class Indexable)
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
class local(object):
    """
    This object will provide the same info as time.timezone, time.altzone,
    time.daylight, and time.tzname. Note that the time items are variables but
    the nldt.local items are methods and should be called with parentheses.
    """

    # -------------------------------------------------------------------------
    def timezone(self):
        """
        Return the UTC offset for the local standard time (class local)
        """
        return time.timezone

    # -------------------------------------------------------------------------
    def altzone(self):
        """
        Return the UTC offset for the local time during DST (class local)
        """
        return time.altzone

    # -------------------------------------------------------------------------
    def daylight(self):
        """
        Return 1 if DST info is defined for the local timezone (class local)
        """
        return time.daylight

    # -------------------------------------------------------------------------
    def tzname(self):
        """
        Return tuple of standard and DST timezone abbreviation (class local)
        """
        return time.tzname


# -----------------------------------------------------------------------------
class moment(object):
    """
    Objects of this class represent a point in time. The moment is stored in
    UTC. The strptime formats in list moment.formats are used to intuit the
    format of date/time strings for which no format is provided.
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
    @classmethod
    def default_tz(cls, value=None):
        """
        If *value* is None, return the currently set default timezone. If
        *value* is not None, use it to set the default timezone for
        interpreting inputs to the moment constructor (other than epoch values)
        (class moment)
        """
        if hasattr(cls, 'deftz'):
            rval = cls.deftz
        else:
            loc = get_localzone()
            rval = loc.zone
            cls.deftz = rval
        if value == 'clear':
            del cls.deftz
        elif value:
            cls.deftz = value
        return rval

    # -------------------------------------------------------------------------
    @classmethod
    def takes_tz(cls, value):
        """
        Returns True if a tz arg can be passed to the moment constructor for
        this *value* as a date/time specification. (class moment)
        """
        return any([isinstance(value, time.struct_time),
                    isinstance(value, tuple),
                    isinstance(value, str) and not value.isdigit()])

    # -------------------------------------------------------------------------
    def __init__(self, dspec=None, fmt=None, itz=None):
        """
        Constructs a moment object.

        *dspec*: A date/time specification. May be
          - a number
          - a number represented in a string
          - an already instantiated moment
          - a time.struct_time as returned by time.localtime or time.gmtime
          - a tuple containing between 6 and 9 number values
          - a string representing a date and/or time

        The first three (number, number in a string, or an already instantiated
        moment) represent a UTC epoch (i.e., the number of seconds since
        midnight January 1, 1970) and therefore never get a timezone
        adjustment.

        The last three (time.struct_time, tuple, or date/time string) can
        represent a time in any timezone. By default, the timezone offset local
        at runtime is used to adjust the time value before storing it in the
        moment.

        *fmt*: A string containing strftime-style format codes used to
        interpret a *dspec* of type str.

        *itz*: A timezone used to convert the time in a time.struct_time,
        tuple, or date/time string (i.e., *dspec* is not one of the number
        types). If this is not specified, the default timezone. The default
        timezone will be the timezone configured to be local on the host
        computer unless class method moment.default_tz() is called to change
        it.

        Examples:
            >>> import nldt
            # current time
            >>> now = nldt.moment()
            >>> now()
            '2016-12-04'
            # format intuited
            >>> new_year_day = nldt.moment('2001-01-01')
            >>> new_year_day()
            '2001-01-01'
            # specified format
            >>> then = nldt.moment('Dec 29 2016', '%b %m %Y')
            >>> then()
            '2016-12-29'

        (class moment)
        """
        # messages
        no_args = 'moment() cannot take format or tz without date spec'
        epc_no_fmt_tz = 'moment(epoch) does not take timezone or format'
        fmt_str = 'moment() cannot take format when date is not of type str'
        tuplen = 'need at least 6 values, no more than 9'
        valid_calls = "\n".join(["Valid ways of calling nldt.moment():",
                                 "    nldt.moment()",
                                 "    nldt.moment(<epoch-seconds>)",
                                 "    nldt.moment('YYYY-mm-dd')",
                                 "    nldt.moment(<date-str>[, <format>])"])

        if not hasattr(self.__class__, 'deftz'):
            self.__class__.deftz = 'local'
        self.moment = None
        if dspec is None:
            if itz or fmt:
                raise InitError(no_args)
            else:
                self.moment = int(time.time())
        elif any([isinstance(dspec, numbers.Number),
                  isinstance(dspec, str) and dspec.isdigit(),
                  isinstance(dspec, moment)
                  ]):
            if itz or fmt:
                raise ValueError(epc_no_fmt_tz)
            elif isinstance(dspec, moment):
                self.moment = dspec.epoch()
            else:
                self.moment = int(dspec)
        elif isinstance(dspec, time.struct_time):
            if fmt:
                raise InitError(fmt_str)
            if itz:
                self.moment = self._normalize(timegm(dspec), tz=itz)
            else:
                self.moment = self._normalize(timegm(dspec),
                                              tz=self.__class__.deftz)
        elif isinstance(dspec, tuple):
            if fmt:
                raise InitError(fmt_str)
            if 6 <= len(dspec) <= 9:
                if itz:
                    self.moment = self._normalize(timegm(dspec), tz=itz)
                else:
                    self.moment = self._normalize(timegm(dspec),
                                                  tz=self.__class__.deftz)
            else:
                raise ValueError(tuplen)
        elif isinstance(dspec, str):
            if fmt:
                fmt = fmt.replace("%F", "%Y-%m-%d")
                fmt = fmt.replace("%T", "%H:%M:%S")
                when = timegm(time.strptime(dspec, fmt))
                if itz:
                    self.moment = self._normalize(when, tz=itz)
                else:
                    self.moment = self._normalize(when,
                                                  tz=self.__class__.deftz)
            elif itz:
                self.moment = self._normalize(self._guess_format(dspec),
                                              tz=itz)
            else:
                self.moment = self._normalize(self._guess_format(dspec),
                                              tz=self.__class__.deftz)
        else:
            raise ValueError(valid_calls)

    # -------------------------------------------------------------------------
    def __call__(self, fmt=None, otz=None):
        """
        Returns a string representing the date/time of the epoch value stored
        in self.

        *fmt*: Optional string indicating the desired output format.

        *otz*: Optional timezone indicating that the date/time in the output
        string should be localized to the specified timezone.

        Examples:
            >>> import nldt
            >>> a = nldt.moment()
            # No arguments, the default format is the ISO date
            >>> a()
            '2016-12-04'

            # *format* specified
            >>> a('%Y.%m%d %H:%M:%S')
            '2016.1204 07:16:20'

        (class moment)
        """
        fmt = fmt or "%Y-%m-%d"
        otz = otz or 'local'
        if otz == 'local':
            tm = time.localtime(self.moment)
        elif otz.lower() == 'utc':
            tzset('UTC+00UTC+00')
            tm = time.gmtime(self.moment)
        else:
            offset = duration(seconds=utc_offset(self.moment, otz))
            tm = time.gmtime(self.moment + offset.seconds)
            fmt = fmt.replace('%Z', tzname(tz=otz, epoch=self.moment))
            fmt = fmt.replace('%z', offset("%H%M"))
        rval = time.strftime(fmt, tm)
        tzset(None)
        return rval

    # -------------------------------------------------------------------------
    def __add__(self, other):
        """
        Add *other* to *self*
            moment + duration => moment
            moment + number-of-seconds => moment
            moment + moment => exception
        (class moment)
        """
        if isinstance(other, duration):
            rval = moment(self.epoch() + other.seconds)
        elif isinstance(other, numbers.Number):
            rval = moment(self.epoch() + other)
        elif isinstance(other, moment):
            raise TypeError("sum of moments is not defined")
        else:
            raise TypeError("unsupported operand type(s) for +: '{}' and '{}'"
                            .format(type(self), type(other)))
        return rval

    # -------------------------------------------------------------------------
    def __eq__(self, other):
        """
        Returns True or False - whether two moment objects are equal
        implicit

        *other*: a second moment object to be compared to self

        Examples:
            >>> import nldt

            # instantiated seconds apart, a and b will not be equal
            >>> a = nldt.moment()
            >>> b = nldt.moment()
            >>> a == b
            False

            # however, once they are both advanced to the beginning of
            # tomorrow, so they both record the beginning of the day at
            # midnight, they will be equal
            >>> prs = nldt.Parser()
            >>> a = prs('tomorrow', a)
            >>> b = prs('tomorrow', b)
            >>> a == b
            True
        (class moment)
        """
        if isinstance(other, moment):
            rval = (self.epoch() == other.epoch())
        elif isinstance(other, numbers.Number):
            rval = (self.epoch() == int(other))       # nocov
        elif isinstance(other, str):
            if other.isdigit():
                rval = (self.epoch == int(other))     # nocov
            else:
                othm = moment(other)
                rval = (self.epoch() == othm.epoch())
        # vvv nocov vvv
        elif isinstance(other, time.struct_tm):
            othm = timegm(other)
            rval = (self.epoch() == othm.epoch())
        elif isinstance(other, tuple):
            if 6 <= len(other) <= 9:
                othm = timegm(other)
                rval = (self.epoch() == othm.epoch())
            else:
                raise ValueError('need at least 6 values, no more than 9')
        # ^^^ nocov ^^^
        return rval

    # -------------------------------------------------------------------------
    def __sub__(self, other):
        """
        Returns the difference of *self* and *other*. The result type depends
        on the type of the subtrahend:
            moment - moment => duration
            moment - duration => moment
            moment - number-of-seconds => moment
            moment - anything-else => undefined
        (class moment)
        """
        if isinstance(other, moment):
            rval = duration(seconds=(self.epoch() - other.epoch()))
        elif isinstance(other, numbers.Number):
            rval = moment(self.epoch() - other)
        elif isinstance(other, duration):
            rval = moment(self.epoch() - other.seconds)
        else:
            raise ValueError("Invalid subtrahend for moment subtraction")
        return rval

    # -------------------------------------------------------------------------
    def __repr__(self):
        """
        Returns a string that will regenerate this object if passed to eval()

        Examples:
            >>> import nldt
            >>> c = nldt.moment()
            >>> assert eval(repr(c)) == c
            True
            >>> print repr(c)
            nldt.moment(1481000400)
        (class moment)
        """
        rval = "nldt.moment({:d})".format(int(self.moment))
        return rval

    # -------------------------------------------------------------------------
    def __str__(self):
        """
        Returns a human-readable representation of this object

        Examples:
            >>> import nldt
            >>> c = nldt.moment()
            >>> print(c)
            2016-12-04 07:31:08
        (class moment)
        """
        return time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(self.moment))

    # -------------------------------------------------------------------------
    def _guess_format(self, spec):
        """
        Tries each of the parse formats in the list until one works or the list
        is exhausted. Returns the UTC epoch (or None if we don't find a
        matching format). (class moment)
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
            raise ValueError("None of the common specifications match "
                             "the date/time string")

    # -------------------------------------------------------------------------
    def _normalize(self, when, tz):
        """
        Apply the appropriate UTC offset for the specified timezone *tz* to
        *when* (class moment)
        """
        offset = utc_offset(epoch=when, tz=tz)
        return when - offset

    # -------------------------------------------------------------------------
    def _validate(self, unit, start):
        """
        If *unit* is not 'week' and *start* is not None, raise an exception. If
        start is not a weekday, raise an exception (class moment)
        """
        wk = week()
        if start:
            if unit != 'week':
                raise ValueError(txt['start_inv01'])
            elif all([start not in x for x in wk.day_list()]):
                raise ValueError(txt['start_inv02'])

    # -------------------------------------------------------------------------
    def asctime(self, tz=None):
        """
        Format the UTC time as '%a %b %d %T %Y'. (class moment)
        """
        tz = tz or 'UTC'
        rval = time.strftime('%c', self.localtime(tz=tz))
        return rval

    # -------------------------------------------------------------------------
    def ctime(self, **kw):
        """
        This is an alias for self.asctime() (class moment)
        """
        return self.asctime(**kw)

    # -------------------------------------------------------------------------
    def epoch(self):
        """
        Returns the currently stored moment as an int UTC epoch

        Examples:
            >>> import nldt
            >>> q = nldt.moment()
            >>> q.epoch()
            1480855032

        (class moment)
        """
        return int(self.moment)

    # -------------------------------------------------------------------------
    def gmtime(self):
        """
        Returns the UTC tm structure for the currently stored moment

        examples:
            >>> import nldt
            >>> q = nldt.moment()
            >>> q.gmtime()
            time.struct_time(tm_year=2016, tm_mon=12, tm_mday=4, tm_hour=7,
            tm_min=37, tm_sec=12, tm_wday=6, tm_yday=339, tm_isdst=0)

        (class moment)
        """
        return time.gmtime(self.moment)

    # -------------------------------------------------------------------------
    def localtime(self, tz=None):
        """
        Returns the local time tm structure for the stored moment

        examples:
            >>> import nldt
            >>> q = nldt.moment()
            >>> q.localtime()
            time.struct_time(tm_year=2016, tm_mon=12, tm_mday=4, tm_hour=7,
            tm_min=37, tm_sec=12, tm_wday=6, tm_yday=339, tm_isdst=0)

        (class moment)
        """
        with tz_context(tz):
            rval = time.localtime(self.moment)
        return rval

    # -------------------------------------------------------------------------
    def ceiling(self, unit, start=None):
        """
        Computes the ceiling of *unit* (second, minute, hour, day, etc.) from
        *self*.epoch()

        (class moment)
        """
        wk = week()
        self._validate(unit, start)
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
            start = start or 'monday'
            delta = (6 + wk.index(start) - tm.tm_wday) % 7
            ceil = timegm((tm.tm_year, tm.tm_mon, tm.tm_mday + delta,
                           23, 59, 59, 0, 0, 0))
        elif unit == 'month':
            maxday = month().days(year=tm.tm_year, month=tm.tm_mon)
            ceil = timegm((tm.tm_year, tm.tm_mon, maxday,
                           23, 59, 59, 0, 0, 0))
        elif unit == 'year':
            ceil = timegm((tm.tm_year, 12, 31, 23, 59, 59, 0, 0, 0))
        else:
            raise ValueError("'{}' is not a time unit".format(unit))
        return moment(ceil)

    # -------------------------------------------------------------------------
    def floor(self, unit, start=None):
        """
        Computes the floor of *unit* (second, minute, hour, day, etc.) from
        *self*.epoch()

        (class moment)
        """
        wk = week()
        self._validate(unit, start)
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
            start = start or 'monday'
            tm = time.gmtime(epoch)
            delta = (7 + tm.tm_wday - wk.index(start)) % 7
            floor = timegm((tm.tm_year, tm.tm_mon, tm.tm_mday - delta,
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
            raise ValueError("'{}' is not a time unit".format(unit))
        return rval

    # -------------------------------------------------------------------------
    def time(self):
        """
        Alias for self.epoch() (class moment)
        """
        return self.epoch()

    # -------------------------------------------------------------------------
    def week_floor(self):
        """
        Finds the beginning of the week in which *self*.moment occurs and
        return a new moment object that stores that point in time. (class
        moment)
        """
        return self.floor('week')


# -----------------------------------------------------------------------------
class month(Indexable):
    """
    Defines and serves information about months
    """
    # -------------------------------------------------------------------------
    def __init__(self):
        """
        Set up month info (class month)
        """
        self._dict = {}
        for midx in range(1, 13):
            date = "2010.{:02d}01".format(midx)
            q = moment(date, itz='utc')
            mname = q('%B', otz='utc').lower()
            abbr = mname[0:3]
            this = {'name': mname,
                    'abbr': abbr,
                    'idx': midx,
                    'days': self._days(midx)
                    }
            self._dict[abbr] = this
            self._dict[midx] = this

    # -------------------------------------------------------------------------
    def days(self, month, year=None):
        """
        Returns the number of days in the indicated *month*. If *year* is not
        specified, the current year is used. (class month)
        """
        month = self.indexify(month)              # noqa: F821
        rval = self._dict[month]['days']
        if month == 2 and self.isleap(year):
            rval += 1
        return rval

    # -------------------------------------------------------------------------
    def _days(self, midx):
        """
        This is a private function returning the number of days in each month,
        based on the year 2010. It is used for setting up self._dict. (class
        month)
        """
        q = moment("2010.{:02d}01".format((midx % 12) + 1))
        p = moment(q.moment - 24 * 3600)
        rval = int(p('%d'))
        return rval

    # -------------------------------------------------------------------------
    def index(self, name_or_idx):
        """
        Given a month name or index in *name_or_idx*, this returns the index of
        the month in the range 1 .. 12 or throws a ValueError. (class month)
        """
        midx = self.indexify(name_or_idx)
        return self._dict[midx]['idx']

    # -------------------------------------------------------------------------
    def isleap(self, year=None):
        """
        Returns true if *year* is leap. If *year* is not provided, return True
        if the current year is leap, else False. (class month)
        """
        if year is None:
            rval = False
        else:
            rval = (year % 4 == 0 and year % 100 != 0) or year % 400 == 0
        return rval

    # -------------------------------------------------------------------------
    def names(self):
        """
        Returns a list of lowercase full month names (class month)
        """
        return [self._dict[x]['name'] for x in self._dict
                if isinstance(x, int)]

    # -------------------------------------------------------------------------
    def short_names(self):
        """
        Returns a list of three letter lowercase month name abbreviations
        (class month)
        """
        return [self._dict[x]['abbr'] for x in self._dict
                if isinstance(x, int)]

    # -------------------------------------------------------------------------
    def match_monthnames(self):
        """
        Returns a regex that will match all month names (class month)
        """
        rgx = "(" + "|".join([self._dict[x]['name'] for x in self._dict
                              if isinstance(x, int)]) + ")"
        return rgx


# -----------------------------------------------------------------------------
class Parser(object):
    """
    This class provides a method object whose __call__() method will examine
    its input to determine the correct submethod(s) to do the work or parsing
    the input.
    """
    # -------------------------------------------------------------------------
    def __init__(self):
        """
        Sets up the Parser object (class Parser)
        """
        self.preps = prepositions()
        self.tu = time_units()
        self.wk = week()
        self.mon = month()
        self.wkday_rgx = self.wk.match_weekdays()

    # -------------------------------------------------------------------------
    def __call__(self, expr, start=None):
        """
        Parses *expr*, using *start* as the initial reference point if
        provided. (class Parser)
        """
        expr = expr.replace("earlier", "ago")
        expr = expr.replace("later", "from now")

        result = []
        start = start or moment()
        if self.research("\s(of|in)\s", expr, result):
            rval = self.parse_of_in(expr, result[0].group(), start)
        elif expr.strip().lower() in self.mon.names():
            rval = self.parse_mon_name(expr, start)
        elif expr in ['yesterday', 'today', 'now', 'tomorrow']:
            rval = self.parse_yestermorrow(expr, start)
        elif 'ago' in expr:
            rval = self.parse_ago(expr, start)
        elif 'from now' in expr:
            rval = self.parse_from_now(expr, start)
        elif self.research("(\s|^)month(\s|$)", expr, result):
            rval = self.parse_month(expr, start)
        elif self.research("(\s|^)week(\s|$)", expr, result):
            rval = self.parse_week(expr, start)
        elif self.research("(\s|^)year(\s|$)", expr, result):
            rval = self.parse_year(expr, start)
        elif self.research(self.wkday_rgx, expr, result):
            rval = self.parse_weekday(expr, result, start)
        else:
            msg = ("Failure parsing '{}'".format(expr)
                   + " -- not recognized as a time expression")
            raise ParseError(msg)
        return rval

    # -------------------------------------------------------------------------
    def parse_of_in(self, expr, prep, start):
        """
        Handles expressions like 'third of May', 'first week in June' (class
        Parser)
        """
        unit = self.tu.find_unit(expr)
        pre, post = expr.split(prep)
        rval = self(post)
        if pre == 'end' and unit:
            rval = rval.ceiling(unit)
        elif pre == 'beginning':
            pass
        else:
            rval = self(pre, rval)
        return rval

    # -------------------------------------------------------------------------
    def parse_mon_name(self, expr, start):
        """
        Handles expressions like 'May', 'October', 'February, 1933' (class
        Parser)
        """
        rval = moment()
        tm = rval.gmtime()
        midx = self.mon.index(expr)
        return moment((tm.tm_year, midx, 1, 0, 0, 0, 0, 0, 0))

    # -------------------------------------------------------------------------
    def parse_ago(self, expr, start):
        """
        Handle expressions like 'a week ago', 'three days ago', 'five years
        ago', etc. (class Parser)
        """
        nums = numberize.scan(expr)
        if isinstance(nums[0], int):
            count = nums[0]
        else:
            count = 1
        unit = self.tu.find_unit(expr)
        if unit is None:
            raise ValueError("No unit found in expression '{}'".format(expr))
        rval = moment()
        rval = moment(rval.epoch() - count * self.tu.magnitude(unit))
        return rval

    # -------------------------------------------------------------------------
    def parse_from_now(self, expr, start):
        """
        Handle expressions like 'an hour from now', 'two days from now', 'four
        weeks from now', 'three years from now', etc. (class Parser)
        """
        nums = numberize.scan(expr)
        if isinstance(nums[0], int):
            count = nums[0]
        else:
            count = 1
        unit = self.tu.find_unit(expr)
        if unit is None:
            raise ValueError("No unit found in expression '{}'".format(expr))
        rval = moment()
        rval = moment(rval.epoch() + count * self.tu.magnitude(unit))
        return rval

    # -------------------------------------------------------------------------
    def parse_month(self, expr, start):
        """
        Handle 'next month', 'last month' (class Parser)
        """
        wb = word_before('month', expr)
        if wb == 'last':
            day_mag = self.tu.magnitude('day')
            floor = start.floor('month').epoch()
            rval = moment(floor - day_mag).floor('month')
        elif wb == 'next':
            week_mag = self.tu.magnitude('week')
            ceil = start.ceiling('month').epoch()
            rval = moment(ceil + week_mag).floor('month')
        return rval

    # -------------------------------------------------------------------------
    def parse_week(self, expr, start):
        """
        Various expressions that involve 'week' (class Parser)
        """
        wb = word_before('week', expr)
        if wb == 'last':
            flr = start.week_floor().epoch()
            rval = moment(flr - self.tu.magnitude('week'))
        elif wb == 'next':
            flr = start.week_floor().epoch()
            rval = moment(flr + self.tu.magnitude('week'))
        elif wb == 'first':
            tm = start.gmtime()
            delta = (7 - tm.tm_wday) % 7
            rval = moment(timegm((tm.tm_year, tm.tm_mon, tm.tm_mday + delta,
                                  0, 0, 0, 0, 0, 0)))
        elif wb == 'the' or wb == 'this':
            rval = start.week_floor()
        elif wb in self.wk.day_list():
            start = self('next {}'.format(wb))
            rval = self('next {}'.format(wb), start)
        elif expr == 'week after next':
            rval = self('next week')
            rval = self('next week', rval)
        elif expr == 'week before last':
            rval = self('last week')
            rval = self('last week', rval)
        return rval

    # -------------------------------------------------------------------------
    def parse_year(self, expr, start):
        """
        Parse expressions like 'last year', 'next year' (class Parser)
        """
        wb = word_before('year', expr)
        if wb == 'last':
            then = "{}-01-01".format(int(start("%Y")) - 1)
            rval = moment(then)
        elif wb == 'next':
            then = "{}-01-01".format(int(start("%Y")) + 1)
            rval = moment(then)
        return rval

    # -------------------------------------------------------------------------
    def parse_weekday(self, expr, result, start):
        """
        Parse expressions like 'next monday', 'last wednesday', etc. (class
        Parser)
        """
        wday = result[0].group()
        wb = word_before(wday, expr)
        if wb == 'next':
            swd = start('%A').lower()
            delta = self.wk.forediff(swd, wday) or 7
            rval = moment(start.epoch() + delta * self.tu.magnitude('day'))
        elif wb == 'last':
            swd = start('%A').lower()
            delta = self.wk.backdiff(swd, wday) or 7
            rval = moment(start.epoch() - delta * self.tu.magnitude('day'))
        return rval

    # -------------------------------------------------------------------------
    def parse_yestermorrow(self, expr, start):
        """
        Handle 'yesterday', 'today', 'tomorrow'. Decided that 'today' should
        return the same as 'now' and that 'yesterday' and 'tomorrow' are offset
        from now by a day's magnitude in opposite directions. The other option
        would be to have each of these resolve to the floor of a day. If floor
        is what is desired, we can always do m = <parser>('today').floor().
        (class Parser)
        """
        if expr == 'yesterday':
            rval = moment(start.epoch() - self.tu.magnitude('day'))
        elif expr in ['today', 'now']:
            rval = start
        elif expr == 'tomorrow':
            rval = moment(start.epoch() + self.tu.magnitude('day'))
        return rval

    # -------------------------------------------------------------------------
    def research(self, pattern, text, result):
        """
        Looks for *pattern* in *text*. If something is found, push the search
        object into *result* (which must be a list) and also return it. (class
        Parser)
        """
        if not isinstance(result, list):
            raise TypeError("result must be an empty list")
        q = re.search(pattern, text)
        if q:
            result.append(q)
        return q


# -----------------------------------------------------------------------------
class prepositions(object):
    """
    Provides information and tools for finding and interpreting prepositions in
    natural language time expressions
    """
    # -------------------------------------------------------------------------
    def __init__(self):
        """
        Sets up the prepositions object. In the self.preps dict, the keys are
        the recognized prepositions and the values indicate the temporal
        direction of the key -- +1 for forward in time, -1 for backward. (class
        prepositions)
        """
        self.preps = {'of': 1, 'in': 1, 'from': 1, 'after': 1, 'before': -1}

    # -------------------------------------------------------------------------
    def split(self, text):
        """
        Constructs (and caches) a regex based on the prepositions and use it to
        split *text*, returning the list of pieces. (class prepositions)
        """
        if not hasattr(self, 'regex'):
            self.regex = "\\s(" + "|".join(self.preps.keys()) + ")\\s"
        rval = re.split(self.regex, text)
        if len(rval) < 2:
            return None, rval
        else:
            return rval[1], rval

    # -------------------------------------------------------------------------
    def are_in(self, text):
        """
        Returns True if *text* contains any prepositions (class prepositions)
        """
        return any([x in self.preps for x in text.split()])

    # -------------------------------------------------------------------------
    def direction(self, prep):
        """
        Returns the direction for preposition *prep* (class prepositions)
        """
        return self.preps[prep]


# -----------------------------------------------------------------------------
class time_units(object):
    """
    Provides information about time units
    """
    # -------------------------------------------------------------------------
    def __init__(self):
        """
        Sets up the list of units with the number of seconds in each (class
        time_units)
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
        Scans *text* and return the first unit found or None (class time_units)
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
        (class time_units)
        """
        return self.units.get(unit, -1)

    # -------------------------------------------------------------------------
    def unit_list(self):
        """
        Returns the list of units (class time_units)
        """
        return self.units.keys()


# -----------------------------------------------------------------------------
class week(Indexable):
    """
    Defines and serves weekday information
    """
    # -------------------------------------------------------------------------
    def __init__(self):
        """
        Sets up week info (class week)
        """
        self._dict = {}
        for idx in range(0, 7):
            q = moment("2018.01{:02d}".format(idx+1))
            wname = q('%A', otz='utc').lower()
            abbr = wname[0:3]
            this = {'name': wname,
                    'abbr': abbr,
                    'idx': idx,
                    }
            self._dict[abbr] = this
            self._dict[idx] = this

    # -------------------------------------------------------------------------
    def day_list(self):
        """
        Returns a list of weekday names (class week)
        """
        return [self._dict[x]['name'] for x in self._dict
                if isinstance(x, int)]

    # -------------------------------------------------------------------------
    def find_day(self, text):
        """
        Finds and returns the first weekday name in *text* (class week)
        """
        found = [wday for wday in self.day_list()
                 if re.search("(^|\W){}(\W|$)".format(wday),
                              text,
                              re.IGNORECASE)]
        if found:
            return found[0]
        else:
            return None

    # -------------------------------------------------------------------------
    def forediff(self, start, end):
        """
        Returns the number of days required to get from day *start* to day
        *end* going forward. *start* and *end* can be day names or index
        values. (class week)
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
        Returns the number of days required to get from day *start* to day
        *end* going forward. *start* and *end* can be day names or index
        values. (class week)
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
        Returns the numeric index for *wday* (mon = 0, tue = 1, ... sun = 6)
        (class week)
        """
        if 3 < len(wday):
            wday = wday[0:3].lower()
        return self._dict[wday]['idx']

    # -------------------------------------------------------------------------
    def fullname(self, idx_or_abbr):
        """
        Looks up *idx_or_abbr* in self._dict and return the 'name' item (class
        week)
        """
        idx = self.indexify(idx_or_abbr)
        return self._dict[idx]['name']

    # -------------------------------------------------------------------------
    def match_weekdays(self):
        """
        Returns a regex that will match all weekdays (class week)
        """
        return "(mon|tues|wednes|thurs|fri|satur|sun)day"

    # -------------------------------------------------------------------------
    def day_number(self, moment_or_epoch, count=None):
        """
        This returns a weekday number based on a moment or epoch time. The
        *count* argument can be one of

          * 'mon0' (the default) => mon = 0 ... sun = 6
          * 'sun0' => sun = 0 ... sat = 6
          * 'mon1' => mon = 1 ... sun = 7

        'mon0' is the counting regime used in the tm structures
        returned by time.localtime() and time.gmtime().

        'sun0' is the counting regime for the '%w' specifier in time.strftime()
        and time.strptime() patterns.

        'mon1' is the counting regime for the '%u' specifier in time.strftime()
        and time.strptime().

        (class week)
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
class Stub(Exception):
    """
    To be raised in stub functions
    """
    # -------------------------------------------------------------------------
    def __init__(self, msg=None):
        fullmsg = "{}() is a stub -- please complete it.".format(caller_name())
        if msg:
            fullmsg += " ({})".format(msg)
        super().__init__(fullmsg)


# -----------------------------------------------------------------------------
class InitError(Exception):
    """
    This exception is for calling out problems in initializing objects
    """
    pass


# -----------------------------------------------------------------------------
class ParseError(Exception):
    """
    This exception is for calling out problems in initializing objects
    """
    pass


# -----------------------------------------------------------------------------
def caller_name():
    """
    Returns the name of the caller of the caller of this function
    """
    return inspect.stack()[2].function


# -----------------------------------------------------------------------------
def clock():
    """
    Alias for time.clock()
    """
    return time.clock()


# -----------------------------------------------------------------------------
def dst(when=None, tz=None):
    """
    Return True or False - daylight savings time is in force or not

    NOTE: If pytz timezone object doesn't have a _utc_transition_times table
    (e.g., the UTC zone), dst is always off.

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
    zone = get_localzone() if tz == 'local' else pytz.timezone(tz)
    try:
        broke = False
        for idx, tdx in enumerate(zone._utc_transition_times):
            try:
                transition_time = zone._utc_transition_times[idx].timestamp()
            except ValueError:
                continue

            if when.epoch() < transition_time:
                broke = True
                break

        if broke:
            rval = (zone._transition_info[idx-1][1].total_seconds() != 0)
        else:
            rval = (zone._transition_info[-1][1].total_seconds() != 0)
        return rval
    except AttributeError:
        return False


# -----------------------------------------------------------------------------
def timezone():
    """
    Returns the locally configured timezone name

    The timezone name may vary with whether DST is in effect or not. The
    example shows a timezone of 'EST' for Eastern Standard Time. At times of
    the year when DST is in effect, the timezone is EDT.

    Examples:
        >>> import nldt
        >>> nldt.timezone()
        EST
    """
    now = time.localtime()
    rval = time.tzname[now.tm_isdst]
    return rval


# -----------------------------------------------------------------------------
def timegm(*args):
    """
    This is a wrapper for calendar.timegm
    """
    return calendar.timegm(*args)


# -----------------------------------------------------------------------------
@contextlib.contextmanager
def tz_context(zone=None):
    """
    This context manager sets the local timezone to *zone* during the yield and
    back to the original setting afterward
    """
    tzorig = os.getenv('TZ')
    if zone:
        zone = pytz.timezone(zone)
    else:
        zone = get_localzone()

    sdt = datetime(2011, 1, 1)
    soff = -1 * int(zone.utcoffset(sdt).total_seconds()/3600)
    ddt = datetime(2011, 7, 1)
    doff = -1 * int(zone.utcoffset(ddt).total_seconds()/3600)
    tzstr = "{}{}{}{}".format(zone.tzname(sdt), soff,
                              zone.tzname(ddt), doff)
    os.environ['TZ'] = tzstr
    time.tzset()

    yield

    if tzorig:
        os.environ['TZ'] = tzorig
    elif 'TZ' in os.environ:
        del os.environ['TZ']
    time.tzset()


# -----------------------------------------------------------------------------
def tzname(tz=None, epoch=None):
    """
    Returns the name of the timezone indicated by *tz*, or the local timezone
    if *tz* is None.
    """
    zone = pytz.timezone(tz) if tz else get_localzone()
    epoch = epoch or moment()
    return zone.tzname(datetime.fromtimestamp(epoch))


# -----------------------------------------------------------------------------
def tzset(zone=None):
    """
    Set os.environ['TZ'] and call time.tzset() to influence time calculations
    """
    if zone:
        os.environ['TZ'] = zone
    elif 'TZ' in os.environ:
        del os.environ['TZ']
    time.tzset()


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
def version():
    """
    Returns the current project version
    """
    return verinfo._version


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
