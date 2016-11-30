import numbers
import re
import time


# -----------------------------------------------------------------------------
def dst():
    """
    Public

    Return True or False, indicating whether or not daylight savings time is in
    force
    """
    now = time.localtime()
    return now.tm_isdst == 1


# -----------------------------------------------------------------------------
def timezone():
    """
    Public

    Return the locally configured timezone name
    """
    now = time.localtime()
    rval = time.tzname[now.tm_isdst]
    return rval


# -----------------------------------------------------------------------------
def tomorrow():
    """
    Public

    Return a when object representing a time 24 hours from now
    """
    rval = when(time.time() + 24*3600)
    return rval


# -----------------------------------------------------------------------------
def yesterday():
    """
    Public

    Return a when object representing a time 24 hours in the past
    """
    rval = when(time.time() - 24*3600)
    return rval


# -----------------------------------------------------------------------------
WEEKDAYS = {'mon': 0, 0: 'mon',
            'tue': 1, 1: 'tue',
            'wed': 2, 2: 'wed',
            'thu': 3, 3: 'thu',
            'fri': 4, 4: 'fri',
            'sat': 5, 5: 'sat',
            'sun': 6, 6: 'sun'}


# -----------------------------------------------------------------------------
def weekday_index(weekday):
    """
    Return the numeric index of *weekday*
    """
    idx = weekday.lower()[0:3]
    rval = WEEKDAYS[idx]
    return rval


# -----------------------------------------------------------------------------
class when(object):
    """
    This class describes objects representing a point in time
    """
    formats = ["%Y.%m%d %H:%M:%S",
               "%Y.%m%d %H:%M",
               "%Y.%m%d %H",
               "%Y.%m%d",
               "%Y-%m-%d %H:%M:%S",
               "%Y-%m-%d %H:%M",
               "%Y-%m-%d %H",
               "%Y-%m-%d",
               "%b %d %Y %H:%M:%S",
               "%b %d %Y %H:%M",
               "%b %d %Y %H",
               "%b %d %Y",
               "%b %d, %Y %H:%M:%S",
               "%b %d, %Y %H:%M",
               "%b %d, %Y %H",
               "%b %d, %Y",
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
        Expected, optional arguments are:
         - a time offset or specification (e.g., 'yesterday', 'tomorrow', 'next
           week', 'Dec 3 1972', an epoch time)
         - a parsing format
        """
        if len(args) < 1:
            self.moment = time.time()
        elif len(args) < 2:
            if type(args[0]) == str:
                self.moment = self.parse(args[0])
            elif isinstance(args[0], numbers.Number):
                self.moment = float(args[0])
        else:
            self.moment = time.mktime(time.strptime(args[0], args[1]))

    # -------------------------------------------------------------------------
    def __call__(self, format=None):
        """
        Return a string containing the stored time according to *format*. If
        *format* is None, we use ISO format
        """
        format = format or "%Y-%m-%d %H:%M:%S"
        rval = time.strftime(format, time.localtime(self.moment))
        return rval


    # -------------------------------------------------------------------------
    def dst(self):
        """
        Return True or False to indicate whether Daylight Savings Time is in
        force on the stored date
        """
        tm = time.localtime(self.moment)
        return tm.tm_isdst == 1

    # -------------------------------------------------------------------------
    def epoch(self):
        """
        Return the stored date as an epoch time
        """
        return self.moment

    # -------------------------------------------------------------------------
    def localtime(self):
        """
        Return the tm structure for the stored moment
        """
        return time.localtime(self.moment)

    # -------------------------------------------------------------------------
    def parse(self, spec):
        """
        Figure out what spec means
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

        weekday_rgx = '(mon|tue|wed|thu|fri|sat|sun)'
        if spec == 'tomorrow':
            rval = time.time() + 24*3600
        elif spec == 'yesterday':
            rval = time.time() - 24*3600
        elif 'next' in spec:
            ml = re.findall(weekday_rgx, spec)
            if ml:
                weekday = WEEKDAYS[ml[0]]
            now = time.localtime()
            diff = (7 + weekday - now.tm_wday - 1) % 7 + 1
            rval = time.time() + diff*24*3600
        elif 'last' in spec:
            ml = re.findall(weekday_rgx, spec)
            if ml:
                weekday = WEEKDAYS[ml[0]]
            now = time.localtime()
            diff = (7 + now.tm_wday - weekday - 1) % 7 + 1
            rval = time.time() - diff*24*3600
        elif spec.endswith('week'):
            ml = re.findall(weekday_rgx, spec)
            if ml:
                weekday = WEEKDAYS[ml[0]]
            now = time.localtime()
            diff = (7 + weekday - now.tm_wday - 1) % 7 + 1
            rval = time.time() + (7+diff)*24*3600
        return rval

    # -------------------------------------------------------------------------
    def tomorrow(self):
        """
        Return a when object containing a 24 hour offset from the stored moment
        """
        rval = when(self.moment + 24*3600)
        return rval

    # -------------------------------------------------------------------------
    def yesterday(self):
        """
        Return a when object containing a 24 hour offset from the stored moment
        """
        rval = when(self.moment - 24*3600)
        return rval
