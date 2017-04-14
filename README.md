This module provides a couple of classes that allow for easy access to
date/time functionality. The moment class represents a point in time. The
duration class represents a length of time.

The module also includes a command line script (or will eventually) for
accessing the functionality provided by the library from the command line.

Internally, moments and durations are stored as a floating point number of
seconds. Points in time (moment instances) are stored as the number of
seconds since midnight at the beginning of January 1, 1970. Durations are
stored as the number of seconds in the time interval.

## Quick Start ##

Query the configured timezone

    >>> import nldt
    >>> nldt.timezone()
    'EST'

Check whether Daylight Savings Time is in force now

    >>> nldt.dst()
    False

Check whether Daylight Savings Time is in force on a given date

    >>> nldt.moment('2016-07-01').dst()
    True
    >>> nldt.moment('2016-12-01').dst()
    False

Note that the timezone value will vary with whether DST is in force. For
example, on 2016-07-01,

    >>> nldt.timezone()
    'EDT'

Get the curent time

    >>> now = nldt.moment()
    >>> now()
    2016-11-30

The default display format is ISO. To get the epoch time,

    >>> now.epoch()
    1480482000

The default display format is the ISO date

    >>> now = nldt.moment()
    >>> now()
    2016-11-30

But all the strftime format specifiers are available

    >>> now("%b %d, %Y")
    'Nov 30, 2016'

## Reference ##

An object representing the current moment:

    >>> now = nldt.moment()

Available public methods:

    >>> now()                # __call__(fmt=None)
    '2016-12-03'

The __call__() method with no arguments displays the stored moment as an
ISO date. With a format, the stored moment is formatted according to the
argument:

    >>> now('%D %T')
    '12/03/16 12:27:49'

The __repr__() method produces a string that can be eval'd to unambiguously
generate an identical object:

    >>> a
    nldt.moment(1480786154)

The __str__() method produces a human readable string

    >>> str(a)
    '2016-12-03 12:29:14'

The __eq__() method is defined so that two moment objects based on the same
time index are considered equal.

    >>> a = nldt.moment('2016-12-02')
    >>> b = nldt.moment('yesterday')
    >>> a == b
    True

The dst() method returns True or False to indicate whether Daylight Savings
Time is in force.

    >>> yes = nldt.moment('2016-07-01')
    >>> yes.dst()
    True
    >>> no = nldt.moment('2016-12-01')
    >>> no.dst()
    False

The epoch() method returns the stored moment as an epoch time.

    >>> yes.epoch()
    1467345600

The localtime() method returns the tm tuple for the stored moment.

    >>> yes.localtime()
    time.struct_time(tm_year=2016, tm_mon=7, tm_mday=1,
                     tm_hour=0, tm_min=0, tm_sec=0,
                     tm_wday=4, tm_yday=183, tm_isdst=1)

The timezone() method returns the configured timezone based on whether the
stored time indicates DST is in force.

    >>> yes.timezone()
    'EDT'
    >>> no.timezone()
    'EST'

The parse() method accepts a string argument containing a date/time
specification or a relative time expression in natural language and updates
the stored stored moment to match.

    >>> foo = nldt.moment()
    >>> str(foo)
    '2016-12-03 12:46:38'
    >>> foo.parse('next week')
    >>> str(foo)
    '2016-12-05 00:00:00'
    >>> foo.parse('last friday')
    >>> str(foo)
    '2016-12-02 00:00:00'
    >>> foo.parse('next thursday')
    >>> str(foo)
    '2016-12-08 00:00:00'


## More Tricks ##

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


    now = nldt.moment()
    then = now
    then.update(tomorrow)
    diff = then - now


    now.update('next week')
    now.update('second wednesday of next july')
    now.yesterday()
    now.last_week()
    now.last_month()
    now.parse('end of last month')
    now.last_month('<')
    now.last_month('>')
    now.last_month(

## Contributor Notes ##

 * Functions, methods, and variables whose names begin with alphabetic
   letters and show up in the pydoc output are part of the public API. When
   such routines return a moment or duration, by default they should do so
   in a human-readable format.

 * The prefered human-readable format is the ISO format: %Y-%m-%d
   [%H:%M:%S]

 * Internal functions, methods, and variables, whose names begin with a
   single underscore, generally should expect and return integer epoch
   times.
