## 0.0.4 ...

 * Add tests and support for duration.format()
 * Add tests and support for duration.dhms()
 * Wrap calendar.timegm() in nldt.timegm() so that nldt consumers don't
   have to import calendar.timegm() for themselves
 * Isolated moment-related tests in test_moment.py
 * Isolated duration-related tests from test_nldt.py to test_duration.py
 * Ensure test_early.py runs first by rename it test_0early.py

## 0.0.3 ... 2018.0207 14:34:58

 * 100% test coverage
 * Class tag all the object methods
 * Moment and duration arithmetic:
   * number-of-seconds treated like duration
   * duration + moment produces moment
   * duration + duration produces duration
   * moment +/- duration produces moment
   * moment - moment produces duration
   * duration(start, no end) -> exception
   * duration(end, no start) -> exception
 * Replace 'parse' and friends with class Parser
 * Create and define class duration
 * Stub exception for marking code under construction
 * Corrected misspellings
 * Fixed a bug where on Mondays floor('week') returned the base of last
   week, not floor('day') which it should be

## 0.0.2 ... 2018.0204 14:04:08

 * Docstring improvements
 * When year is not specified, month.isleap() and month.days() should
   assume current year
 * Replace constants and stand-alone functions with a set of utility
   classes that encapsulate domain info -- month, week, time_units,
   prepositions
 * Achieving 100% test coverage uncovered several bugs noted in the commit
   messages

## 0.0.1 ... 2018.0203 07:10:07

 * Add test coverage reporting
 * Add tests to improve code coverage

## 0.0.0 ... 2018.0202 19:13:43

 * Finally have all the tests passing
