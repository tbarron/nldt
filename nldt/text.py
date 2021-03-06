"""
nldt - Natural Language Date/Time support
Copyright (c) 2017 - <the end of time>  Tom Barron
See file LICENSING for details
-------------------------------------------------------------------------------
This module defines strings used in nldt to minimize repetition (DRY).

txt['err-*']      Error messages
txt['exc-*']      Exception names
txt['tz-*']       Timezone names
txt['xpr-*']      Time expressions
txt['*-f']        String contains format spec ('{}')
"""
txt = {}
txt['ABC-noinst'] = "This is an abstract base class -- don't instantiate it."
txt['arg-more'] = "argument must be moment or epoch number"
txt['date01'] = "2010-01-01"
txt['date02'] = "2000-12-31 15:59:59"
txt['date03'] = "2010-12-31"
txt['2010-end'] = "2010-12-31"
txt['2011-begin'] = "2011-01-01"
txt['date04'] = "2012-07-01"
txt['leap-yester'] = "2012-02-28"
txt['leap-today'] = "2012-02-29"

txt['dst-when'] = "dst() 'when' argument must be str, number, or moment"
txt['epc-nofmttz'] = "moment(epoch) does not take timezone or format"

txt['err-abc'] = "This is an abstract base class -- don't instantiate it."
txt['err-argmore'] = "argument must be moment or epoch number"
txt['err-ceilweek'] = "ceiling() only accepts start for unit='week'"
txt['err-notatime'] = ("Failure parsing '{}' -- not recognized as a"
                       " time expression")
txt['err-nounit'] = "No unit found in expression"
txt['err-nounit-f'] = "No unit found in expression '{}'"
txt['err-indxfy'] = "Could not indexify '{}'"
txt['err-indxfy-f'] = "Could not indexify '{}'"
txt['err-indxfy-nof'] = "Could not indexify"

txt['exc-ulerr'] = "UnboundLocalError"

txt['fmt-str'] = "moment() cannot take format when date is not of type str"
txt['inv-subtrahend'] = "Invalid subtrahend for moment subtraction"
txt['invtup'] = "Invalid tm tuple"
txt['iso-date'] = "%Y-%m-%d"
txt['iso-ymdhms'] = "%Y.%m%d %H:%M:%S"
txt['iso-datetime'] = "%Y-%m-%d %H:%M:%S"
txt['mctor-001'] = "If start or end is specified, both must be"
txt['mom-sum'] = "sum of moments is not defined"
txt['nan'] = "not a number"
txt['no-args'] = "moment() cannot take format or tz without date spec"
txt['no-match'] = ("None of the common specifications match"
                   " the date/time string")
txt['no-unit'] = "No unit found in expression '{}'"
txt['not-indxfy'] = "Could not indexify '{}'"
txt['not-empty'] = "result must be an empty list"
txt['not-timeu'] = "'{}' is not a time unit"
txt['optypes-01'] = "Unsupported operand types(s): try 'moment' - 'duration'"
txt['optypes-02'] = "unsupported operand types(s): '{}' and '{}'"
txt['parse-fail'] = ("Failure parsing '{}' -- not recognized as"
                     " a time expression")
txt['start-inv01'] = "start only valid in ceiling/floor when unit='week'"
txt['start-inv02'] = "start must be a weekday name or abbreviation"
txt['stubmsg'] = "{}() is a stub -- please complete it."
txt['tuplen'] = "need at least 6 values, no more than 9"
txt['tz-addis'] = "Africa/Addis_Ababa"
txt['tz-ak'] = "US/Alaska"
txt['tz-est'] = "US/Eastern"
txt['tz-nz'] = "NZ"
txt['utc-offset'] = "utc_offset requires an epoch time or None"
txt['valid-calls'] = "\n".join(["Valid ways of calling nldt.moment():",
                                "    nldt.moment()",
                                "    nldt.moment(<epoch-seconds>)",
                                "    nldt.moment('YYYY-mm-dd')",
                                "    nldt.moment(<date-str>[, <format>])"])
txt['wday-rgx'] = "(mon|tues|wednes|thurs|fri|satur|sun)day"

txt['xpr-4dotw'] = "fourth day of this week"
txt['xpr-5dolw'] = "fifth day of last week"
txt['xpr-lwk'] = "last week"
txt['xpr-nwk'] = "next week"
txt['xpr-nthu'] = "next thursday"
txt['xpr-nfri'] = "next friday"
txt['xpr-tod'] = "the other day"
