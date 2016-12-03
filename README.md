This module provides a couple of classes that allow for easy access to
date/time functionality. The moment class represents a point in time. The
duration class represents a length of time.

The module also includes a command line script for accessing the
functionality provided by the library.

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
    
Get the curent time

    >>> now = when.when()    # set now to current time
    >>> now.epoch()
    1480482529.736714
    
The default display format is ISO

    >>> now = nldt.moment()
    >>> now()
    2016-11-30 00:14:50
    
But all the strftime format specifiers are available

    >>> now("%b %d, %Y")
    'Nov 30, 2016'
    
Some simple offsets (e.g., yesterday, tomorrow) are methods on the object

    >>> now.tomorrow("%Y-%m%d")
    '2016-12-01'
    
when will try to intuit the format of dates passed to it

    >>> later = when.when('Dec 29 2016')
    >>> later()
    '2016-12-29'
    
However, it will also accept a format specification to guide its parsing
(but in this case, the date must match the format)

    >>> later = when.when('Dec 29 2016', "%b %d %Y")
    >>> later()
    '2016-12-29'

Offsets can also be specified as arguments...

    >>> then = nldt.moment("tomorrow")
    >>> then("%Y-%m-%d")
    '2016-12-01'
    
... or natural language expressions

    >>> now.parse("last saturday")
    >>> now()
    '2016-11-26 00:15:30'
    
    >>> then.parse("fri week")     # a week after next friday
    >>> then()
    '2016-12-09 00:15:45'

All the time functions are supported:

    now = when.when()
    now.time()                # same as now.epoch()
    now.clock()               # simply calls time.clock()
    now.sleep()               # calls time.sleep()
    now.gmtime()
    now.localtime()
    now.asctime()
    now.ctime()
    now.mktime()              # same as now.epoch()
    now.strftime(fmt)         # format stored time with *fmt*
    now.strptime(spec, fmt)   # update stored time to *spec* per *fmt*
    now.tzset(timezone)       # convert stored time to new timezone
    
Taking the difference of two points in time produces a duration object

    >>> delta = then - now
    >>> delta.seconds()
    1123133
    
    >>> delta.days()
    12.999224537037037
    
A duration added to a when object produces another when object

    >>> later = then + delta
    >>> later()
    '2016-12-21 00:31:19'
