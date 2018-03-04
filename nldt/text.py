txt = {}
txt['ABC_noinst'] = "This is an abstract base class -- don't instantiate it."
txt['arg_more'] = "argument must be moment or epoch number"
txt['date01'] = "2010-01-01"
txt['date02'] = "2000-12-31 15:59:59"
txt['dst_when'] = "dst() 'when' argument must be str, number, or moment"
txt['epc_nofmttz'] = "moment(epoch) does not take timezone or format"
txt['fmt_str'] = "moment() cannot take format when date is not of type str"
txt['inv_subtrahend'] = "Invalid subtrahend for moment subtraction"
txt['invtup'] = "Invalid tm tuple"
txt['mctor_001'] = "If start or end is specified, both must be"
txt['mom_sum'] = "sum of moments is not defined"
txt['no_args'] = "moment() cannot take format or tz without date spec"
txt['no_match'] = ("None of the common specifications match"
                   " the date/time string")
txt['no_unit'] = "No unit found in expression '{}'"
txt['not_indxfy'] = "Could not indexify '{}'"
txt['not_empty'] = "result must be an empty list"
txt['not_timeu'] = "'{}' is not a time unit"
txt['optypes_01'] = "Unsupported operand types(s): try 'moment' - 'duration'"
txt['optypes_02'] = "unsupported operand types(s): '{}' and '{}'"
txt['parse_fail'] = ("Failure parsing '{}' -- not recognized as"
                     " a time expression")
txt['start_inv01'] = "start only valid in ceiling/floor when unit='week'"
txt['start_inv02'] = "start must be a weekday name or abbreviation"
txt['stubmsg'] = "{}() is a stub -- please complete it."
txt['tuplen'] = "need at least 6 values, no more than 9"
txt['utc_offset'] = "utc_offset requires an epoch time or None"
txt['valid_calls'] = "\n".join(["Valid ways of calling nldt.moment():",
                                "    nldt.moment()",
                                "    nldt.moment(<epoch-seconds>)",
                                "    nldt.moment('YYYY-mm-dd')",
                                "    nldt.moment(<date-str>[, <format>])"])
txt['wday_rgx'] = "(mon|tues|wednes|thurs|fri|satur|sun)day"
