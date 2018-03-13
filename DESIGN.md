
Class moment is the heart of nldt. It contains a point in time stored as an
epoch time. The epoch is 1970-01-01T00:00:00 UTC. Epoch times are
represented as an integer number of seconds since the epoch and are always
in UTC.

The local time for a given timezone is computed as an offset from UTC time.

layer 1: class Indexable, class Stub, InitError, ParseError, isnum, offset_list

layer 2: utc_offset, class month, class week, class time_units,
         caller_name, clock, txt, class local, dst, timezone,
         timegm, tz_context, tzname, tzset, tzstring, word_before

layer 3: class duration, class moment, class prepositions

layer 4: class Parser

layer 5: command line


I'd like to add some bells and whistles to pytz:
 - if utcoffset is called with no argument, use datetime.now()
 - if dst is called with no arg, use datetime.now()
 - if tzname is called with no arg, use datetime.now()
