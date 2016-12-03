This module provides a couple of classes that allow for easy access to
date/time functionality. The moment class represents a point in time. The
duration class represents a length of time.

The module also includes a command line script (or will eventually) for
accessing the functionality provided by the library from the command line.

Internally, moments and durations are stored as a floating point number of
seconds. Points in time (moment instances) are stored as the number of
seconds since midnight at the beginning of January 1, 1970. Durations are
stored as the number of seconds in the time interval.

Query the configured timezone

    >>> import nldt
    >>> nldt.timezone()
    'EST'

Check whether Daylight Savings Time is in force now

    >>> nldt.dst()
    False

Check whether Daylight Savings Time is in force on a given date

    >>> nldt.when('2016-07-01').dst()
    True
    >>> nldt.when('2016-12-01').dst()
    False

Note that when DST is in force, the timezone will change. For example, on
2016-07-01,

    >>> nldt.timezone()
    'EDT'

Get the curent time

    >>> nldt.when().epoch()
    1480757873.157439
    >>> time.time()
    1480757873.994515
    >>> nldt.moment().epoch() - time.time()
    -8.106231689453125e-06

The default display format is the ISO date

    >>> now = nldt.moment()
    >>> now()
    2016-11-30

But all the strftime format specifiers are available

    >>> now("%b %d, %Y")
    'Nov 30, 2016'

Some simple offsets (e.g., yesterday, tomorrow) are available as methods on
the object

    >>> then = now.tomorrow()
    >>> then()
    '2016-12-01'

The nldt module will try to intuit the format of dates passed to it

    >>> later = nldt.moment('Dec 29 2016')
    >>> later()
    '2016-12-29'

However, it will also accept a format specification to guide its parsing
(but in this case, the date spec must match the format)

    >>> later = nldt.moment('Dec 29 2016', "%b %d %Y")
    >>> later()
    '2016-12-29'

    >>> later = nldt.moment('dec 29 2016', '%b %d, %Y')
    Traceback (most recent call last):
     ...
    ValueError: time data 'dec 29 2016' does not match format '%b %d, %Y'

Offsets can also be specified as arguments...

    >>> then = nldt.moment("tomorrow")
    >>> then("%Y-%m-%d")
    '2016-12-01'

... or natural language expressions (these can also be passed to the
constructor)

    >>> now.parse("last saturday")
    >>> now()
    '2016-11-26 00:15:30'

    >>> then.parse("fri week")
    >>> then()
    '2016-12-09 00:15:45'

    >>> now.parse('next month')
    >>> now.parse('next year')
    >>> now.parse('last week')
    >>> now.parse('last month')
    >>> now.parse('last year')
    >>> now.parse('a week ago wednesday')                       !@!
    >>> now.parse('1 month 2 days 3 weeks 4 minutes from sunday')                       !@!
    >>> now.parse('42 hrs 42 seconds ago')                       !@!
    >>> now.parse('now+ 42 days 42 weeks')                       !@!
    >>> now.parse('jan 12')                       !@!
    >>> now.parse('jUlY 28 1996 23:59:59')                       !@!
    >>> now.parse('28th')                       !@!
    >>> now.parse('February 7')                       !@!
    >>> now.parse('mar 4th')                       !@!
    >>> now.parse('next april 3rd')                       !@!
    >>> now.parse('last sep-19')                       !@!
    >>> now.parse('last sep-19 7pm')                       !@!
    >>> now.parse('next july 10th at 19:00')                       !@!
    >>> now.parse('7:30 on the 4th of next month')                       !@!
    >>> now.parse('fifteenth of last month')                       !@!
    >>> now.parse('22nd October 3:42am')                       !@!
    >>> now.parse('31st of dec at 9:30 pm')                       !@!
    >>> now.parse('Tue Apr 03 17:00:00 CST 2007')                       !@!
    >>> now.parse('June 13, 1997')                       !@!
    >>> now.parse('May 5,2001')                       !@!
    >>> now.parse('feb 3 1980')                       !@!
    >>> now.parse('october 7 1993 at midnight')                       !@!
    >>> now.parse('01/01/01')                       !@!
    >>> now.parse('3/4/5')                       !@!
    >>> now.parse('30/2/2000')                       !@!
    >>> now.parse('2/30/01')                       !@!
    >>> now.parse('11/31/05')                       !@!

All the time functions are supported:

    now = when.when()
    now.time()                # same as now.epoch()           !@!
    now.clock()               # simply calls time.clock()     !@!
    now.sleep()               # calls time.sleep()            !@!
    now.gmtime()                                              !@!
    now.localtime()                                           !@!
    now.asctime()                                             !@!
    now.ctime()                                              !@!
    now.mktime()              # same as now.epoch()          !@!
    now.strftime(fmt)         # format stored time with *fmt*   !@!
    now.strptime(spec, fmt)   # update stored time to *spec* per *fmt*  !@!
    now.tzset(timezone)       # convert stored time to new timezone  !@!

Taking the difference of two points in time produces a duration object

    >>> delta = then - now            !@!
    >>> delta.seconds()               !@!
    1123133

    >>> delta.days()                  !@!
    12.999224537037037

A duration added to a when object produces another when object

    >>> later = then + delta         !@!
    >>> later()
    '2016-12-21 00:31:19'

In the strftime specification, '%u' generates the 1-based weekday number
where Monday is the first day of the week.

In the strftime specification, '%w' generates the 0-based weekday number
where Sunday is the first day of the week.

The strftime(3) man page says that in the tm structure, tm_wday is the day
of the week with Sunday == 0.

The python time.localtime() function returns a tm structure with tm_wday
being 0 for Monday through 6 for Sunday.
