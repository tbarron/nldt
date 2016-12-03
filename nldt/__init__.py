import numbers
import pdb
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
def compute_tomorrow(moment=None):
    """
    internal

    Compute tomorrow relative to moment (or now if moment not provided)
    """
    ref = moment or time.time()
    ref += 24*3600
    rval = ref - (ref % (24*3600)) + time.timezone
    return rval


# -----------------------------------------------------------------------------
def end_of_last_week(moment=None):
    """
    Compute the end of last week relative to moment
    """
    ref = moment or time.time()
    ref -= 7*24*3600
    reflt = time.localtime(ref)
    diff = 6 - reflt.tm_wday
    eow = ref + diff*24*3600
    eowlt = time.localtime(eow)
    eow_s = time.strftime("%Y-%m-%d 23:59:59", eowlt)
    rval = time.mktime(time.strptime(eow_s, "%Y-%m-%d %H:%M:%S"))
    return rval

# -----------------------------------------------------------------------------
class moment(object):
    """
    This class describes objects representing a point in time
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
    nldict = {'end of last week': end_of_last_week,
              'tomorrow': compute_tomorrow,
              }

    # -------------------------------------------------------------------------
    def __init__(self, *args):
        """
        Expected, optional arguments are:
         - a time offset or specification (e.g., 'yesterday', 'tomorrow', 'next
           week', 'Dec 3 1972', an epoch time)
         - a parsing format
        """
        if len(args) < 1:
            self.moment = int(time.time())
        elif len(args) < 2:
            if type(args[0]) == str:
                self.moment = None
                self.moment = self.parse_return(args[0])
            elif isinstance(args[0], numbers.Number):
                self.moment = int(args[0])
        else:
            self.moment = int(time.mktime(time.strptime(args[0], args[1])))

    # -------------------------------------------------------------------------
    def __call__(self, format=None):
        """
        Return a string containing the stored time according to *format*. If
        *format* is None, we use ISO format
        """
        format = format or "%Y-%m-%d"
        rval = time.strftime(format, time.localtime(self.moment))
        return rval


    # -------------------------------------------------------------------------
    def __eq__(self, other):
        """
        Two moment objects are equal if their moment attributes are
        """
        return self.moment == other.moment

    # -------------------------------------------------------------------------
    def __repr__(self):
        """
        Return a string that will regenerate this object if eval'd
        """
        rval = "nldt.moment({:d})".format(int(self.moment))
        return rval

    # -------------------------------------------------------------------------
    def __str__(self):
        """
        Return a human-readable representation of this object
        """
        return time.strftime('%Y-%m-%d %H:%M:%S',
                             time.localtime(self.moment))

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
        return int(self.moment)

    # -------------------------------------------------------------------------
    def localtime(self):
        """
        Return the tm structure for the stored moment
        """
        return time.localtime(self.moment)

    # -------------------------------------------------------------------------
    def parse(self, spec):
        """
        public: Set the object's value to the date/time indicated by *spec*

        spec - A date/time specification

        Example:
            foo = when.when()
            foo.parse('2013.0630')
            foo.parse('next friday at 5')
        """
        self.moment = self.parse_return(spec)

    # -------------------------------------------------------------------------
    def end_of_day(self, wday_name=None):
        """
        Compute the end of the indicated day. If not today, we assume 'next'.
        """
        point = self.moment or time.time()
        if wday_name:
            now = time.localtime(point)
            wday_num = WEEKDAYS[wday_name]
            diff = (7 + wday_num - now.tm_wday - 1) % 7 + 1
        else:
            diff = 0
        point_in_day = point + diff*24*3600
        ref = time.localtime(point_in_day)
        fmt = "%Y-%m-%d %H:%M:%S"
        ref_s = time.strftime("%Y-%m-%d 23:59:59", ref)
        anchor = time.strptime(ref_s, fmt)
        rval = time.mktime(anchor)
        return rval

    # -------------------------------------------------------------------------
    def end_of_week(self):
        """
        Compute the end of the week.
        """
        rval = self.end_of_day('sun')
        return rval

    # -------------------------------------------------------------------------
    def end_of_month(self):
        """
        Compute the end of the month.
        """
        rval = None
        return rval

    # -------------------------------------------------------------------------
    def end_of_year(self):
        """
        Compute the end of the year.
        """
        rval = None
        return rval

    # -------------------------------------------------------------------------
    def last_weekday(self, wday_name):
        """
        Compute the epoch time of the indicated future weekday
        """
        wday_num = WEEKDAYS[wday_name]
        ref = self.moment or time.time()
        now = time.localtime(ref)
        diff = (7 + now.tm_wday - wday_num - 1) % 7 + 1
        rval = ref - diff*24*3600
        return rval

    # -------------------------------------------------------------------------
    def last_year(self):
        """
        Compute the epoch time of the indicated past year
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
        """
        wday_num = WEEKDAYS[wday_name]
        now = time.localtime()
        diff = (7 + wday_num - now.tm_wday - 1) % 7 + 1
        rval = time.time() + diff*24*3600
        return rval

    # -------------------------------------------------------------------------
    def next_year(self):
        """
        Compute the epoch time of the indicated future year
        """
        thisyear = time.strftime("%Y")
        nextyear = int(thisyear) + 1
        nxyr_s = "{}-01-01".format(nextyear)
        tm = time.strptime(nxyr_s, "%Y-%m-%d")
        rval = time.mktime(tm)
        return rval

    # -------------------------------------------------------------------------
    def guess_format(self, spec):
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
            return self.nldict[spec](self.moment)

        weekday_rgx = '(mon|tue|wed|thu|fri|sat|sun)'
        if spec == 'yesterday':
            ref = self.moment or time.time()
            yest = ref - 24*3600
            rval = yest - yest % (24*3600) + time.timezone
        elif 'end of' in spec:
            ml = re.findall(weekday_rgx, spec)
            if ml:
                rval = self.end_of_day(ml[0])
            elif 'last week' in spec:
                now = self.moment or time.time()
                tmp = moment(now - 7*24*3600)
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
                    ref -= 7*24*3600
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
                rval = tmp + 7*24*3600
            else:
                rval = None
        return rval

    # -------------------------------------------------------------------------
    def timezone(self):
        """
        """
        lt = time.localtime(self.moment)
        return time.tzname[lt.tm_isdst]

    # -------------------------------------------------------------------------
    def tomorrow(self):
        """
        Return a moment object containing a 24 hour offset from the stored
        point in time
        """
        rval = moment(compute_tomorrow(self.moment))
        return rval

    # -------------------------------------------------------------------------
    def yesterday(self):
        """
        Return a moment object containing a 24 hour offset from the stored
        point in time
        """
        rval = moment(self.moment - 24*3600)
        return rval
