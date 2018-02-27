# Natural Language Date/Time processing #

## Some of the things you can do with nldt ##

### Get the weekday of a given date

    >>> import nldt
    >>> date = nldt.moment("2005-08-04")
    >>> date("%A")
    'Thursday'

### Find the first Sunday in a given month

    >>> import nldt
    >>> base = nldt.moment("2017-09-01")
    >>> wday = int(base("%u"))
    >>> delta = (6 - wday) * 24 * 3600
    >>> target = base + delta
    >>> target("%a %F")
    'Sat 2017-09-02'

### Find the date and weekday N days after or before Y

    >>> import nldt
    >>> Y = nldt.moment("1975-01-23")
    >>> X = Y - 200 * 24 * 3600
    >>> X("%a %F")
    'Sun 1974-07-07'
    >>> Z = Y + 75 * 24 * 3600
    >>> Z("%a %F")
    'Tue 1975-04-08'

### Parse date and time related natural langugae expressions

    >>> import nldt
    >>> P = nldt.Parser()
    >>> m = P('tomorrow')
    >>> str(m)
    '2018-02-28 20:58:01'
    >>> str(P('three days ago'))
    '2018-02-24 20:59:13'
    >>> str(P('next week'))
    '2018-03-05 00:00:00'
    >>> str(P('seven days from now'))
    '2018-03-06 21:18:07 Tue'

## Classes ##

This module provides several classes intended to make date and time
functionality easy to access and use.

 * duration: Represents a length of time. Stored as a number of seconds.
   Can be used to represent the offset between UTC and a given timezone.

 * local: Holds information about the local timezone.

 * moment: Represents a point in time. Always stores its time reference in
   UTC. Can report its stored time in the format and/or timezone requested.

 * month: Holds information about months.

 * Parser: A natural language parser that can convert natural language
   expressions like "first week in January" or "last week" or "next year"
   into moments or durations.

### duration ###

 * The sum or difference of two durations is another duration. The sum of a
   moment and a duration is another moment. The difference of a moment and
   duration is another moment. The difference of two moments is a duration.
   It is not clear what the meaning of a sum of two moments would be, so
   that is undefined.

    * <duration> + <duration> -> <duration>
    * <duration> - <duration> -> <duration>
    * <moment> + <duration> -> <moment>
    * <moment> - <duration> -> <moment>
    * <moment> - <moment> -> <duration>
    * <moment> + <moment> -> UNDEFINED

### local ###
### moment ###

The constructor for the moment class can take input times in several forms.
Any input time that consists of a number or a string containing a number
will be interpreted as an epoch time, which is always in the UTC context.
That is, no timezone offset will be applied to such inputs.

Input times represented as a time.struct_tm, a tuple of 6 to 9 numbers, or
a date/time string will be interpreted in the default timezone unless an
explicit timezone is provided at construction time.

### month ###
### Parser ###


The module will also includes a command line script for command line access
to the functionality provided by the library.

Internally, moments and durations are stored as a floating point number of
seconds. Points in time (moment instances) are stored as the number of
seconds since midnight at the beginning of January 1, 1970 (defined in
UTC). Durations are stored as the number of seconds in the time interval.

## Quick Start ##

    import nldt
    from nldt import moment, duration

Query the timezone configured for the current location

    >>> nldt.timezone()
    'EST'

Check whether Daylight Savings Time is in force now in the currently
configured timezone

    >>> nldt.dst()
    False

Check whether Daylight Savings Time is in force on a given date in a given
timezone. If timezone is not specified, the one configured for the current
location will be used. Both dst() and timezone() can take a moment object
(representing a UTC time) as an argument and will return their result in
terms of that moment in time.

    >>> nldt.dst(moment('2016-07-01'), tz='US/Eastern')
    True
    >>> nldt.dst(moment('2016-12-01'), tz='US/Central')
    False

Note that the short timezone name will vary with whether DST is in force.
For example, on 2016-07-01,

    >>> nldt.timezone(moment('2016-07-01'))
    'EDT'
    >>> nldt.timezone(moment('2016-12-31'))
    'EST'

Get the curent UTC date and time. The __call__ method on a moment object
(i.e., '<obj>()') returns the date stored by the object. By default, the
date is returned in ISO-8601 format (YYYY-mm-dd).

    >>> now = moment()
    >>> now()
    2016-11-30

To get the epoch time,

    >>> now.epoch()
    1480482000

To get the date and time in some other format, simply pass the desired
format as an argument:

    >>> now('%Y-%m-%d %H:%M:%S')
    2016-11-30 08:22:38

To get a local date and time, a timezone must be provided

    >>> now('%Y-%m-%d %H:%M:%S', tz='us/central')
    2016-11-30 02:22:28

The special timezone, 'local', can be used to get the time at the currently
configured location

    >>> now('%Y-%m-%d %H:%M:%S %Z', tz='local')
    2016-11-30 03:22:28 EST

All the strftime format specifiers are available (see 'pydoc
time.strftime')

    >>> now("%b %d, %Y")
    'Nov 30, 2016'

The sum or difference of a moment and a duration is another moment.

    >>> now()
    '2016-07-01'
    >>> then = now + duration(day=1)
    >>> then()
    '2016-07-02'

The duration may also be specified as an integer number of seconds

    >>> later = now - 24 * 3600
    >>> later()
    '2016-06-30'

The difference of two moments is a duration, which is reported by default
in terms of seconds

    >>> d = then - later
    >>> d
    duration(172800)
    >>> d()
    172800

Durations can report themselves in terms of other units

    >>> d('day')
    2.0
    >>> d('hour')
    48.0


## Reference ##

This section will list and describe all the classes and all public methods
for each class.

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
