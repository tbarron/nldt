## 0.0.17

    * Ensure that the default timezone is local for both input (when
      constructing moments) and output (when reporting out the stored
      time). The default timezone can be overridden for input by calling
      moment.default_tz() or by passing the itz argument to the moment
      constructor. The default can be overridden for output by using 'with
      nldt.tz_context' or passing the otz argument to moment.__call__().
    * Put message strings in text.py and use them from there.
    * Move 'class' away from the beginning of docstrings since otherwise
      emacs python-mode indentation is messed up.
    * Ability to reset default timezone to the factory default.
    * Ability for week start to be arbitrary day.
    * Full test coverage for moment.__eq__(), nldt.tzstring(),
      nldt.isnum().
    * Make test case ids more descriptive.
    * Get tz_context() working for all timezones.
    * Test case consolidation, code cleanup.

## 0.0.16

 * Renamed the 'tz' argument to moment.__init__() to 'itz' to indicate that
   the timezone is applied to the *input* date/time spec
 * Renamed the 'tz' argument to moment.__call__() to 'otz' to indicate that
   the timezone is applied to the moment on *output*
 * Add test for nldt.moment.takes_tz() to ensure 100% test coverage.
 * Add a test that tickles the bug where 'with nldt.tz_context()' throws a
   KeyError on exit when 'TZ' is not in the environment. Update the code to
   satisfy the test (thereby fixing the bug).
 * Use nldt.moment.default_tz() to set the default input timezone for tests
   to 'utc' so that it doesn't have to be specified on every moment call.
 * Move the tests for nldt.moment.default_tz() to the end of test_moment.py
   so they don't interfere with other tests.
 * Adding reference info to README.md.

## 0.0.15

 * For duration constructor, interpret moment values in the 'utc' timezone
   context
 * New moment class method takes_tz() to indicate whether a moment arg can
   take a timezone argument or not
 * Adjust tests to assess difference thresholds rather than strict equality
   in some cases
 * Adjust time anchors for correctness and easier maintenance of tests
 * For now, we need explicit utc timezone context specification because we
   don't (yet) have a way of specifying a default timezone context for
   moment construction
 * Update tests to use monotonically increasing numeric test ids
 * Test and code to support moment subtraction
 * Test and code for nldt.moment.default_tz() to set default timezone for
   moment constructor input

## 0.0.14

 * Add test for methods ctime(), asctime() and code to satisfy the test
 * Expand test for nldt.localtime() and update code to satisfy it
 * Shorten test names to fit 80 column line

## 0.0.13

 * Add moment.time() as an alias for alias moment.epoch() (to parallel
   time.time())
 * Add nldt.clock() as an alias for time.clock()
 * Add nldt.duration.sleep() as an alias for time.sleep()

## 0.0.12

 * Update requirements.txt to include pexpect
 * Move numberize.py into nldt to make travis happy

## 0.0.11

 * Add tests for 'nldt now' with and without -z and -f
 * Add copyright/licensing information
 * Add object nldt.object and a test for it
 * Add 'with nldt.timezone(TZNAME)' context manager (had to rename previous
   nldt.timezone function to nldt.localzone)
 * Reordered source code to make it easier to find stuff

## 0.0.10 ...

 * Add nldt command line program, handle 'now', 'today', 'tomorrow',
   'yesterday'
 * Adjust command line argument handling to interpret no arguments as 'now'
 * Fix bug where time.mktime() assumes its input tuple is local time by
   calling tzset() to adjust the local timezone when necessary
 * Fix bug where moment was not initializing itself from a numeric string
 * Fix a bug where no parse branch matches the input
 * In tests, avoid the assumption that 'local' always means 'US/Eastern'

## 0.0.9 ... 2018.0212 10:08:35

 * Move the authoritative project version from ~/version.py to
   ~/nldt/verinfo.py. Add function nldt.version() which returns the current
   project version. Test test_version() verifies that nldt.version()
   returns a 'reasonable' version value (i.e., three dot separated
   numbers). In test_deployable(), the version string is checked against
   the most recent git tag.
 * Make duration objects callable with an optional format, like moment
   objects. Remove obsoleted nldt.hhmm(), test_helpers.py,
   duration.format().

## 0.0.8 ... 2018.0211 18:05:56

 * Make nldt.dst() work for timezones that don't have a transition table in
   the pytz tzinfo object.
 * Travis testing apparently takes place in the UTC timezone.
 * nldt.dst() now looks through the pytz _utc_transition_times table to
   decide whether the DST flag should be on or off for a given timezone at
   a specified moment in time.

## 0.0.7 ... 2018.0211 11:07:35

 * Debugging Travis support -- flake8 has to be installed

## 0.0.6 ... 2018.0211 10:49:56

 * Extended flake8 coverage to all the python files
 * Add travis support

## 0.0.5 ... 2018.0210 13:12:53

 * Check tests for debuggability
 * Compare moments for equality based on int epoch, not float moment
 * Test 'yesterday', 'tomorrow' parsing around leap dates
 * Timezones are supported on input and output. That is, the moment
   constructor will accept a timezone and convert the input time to UTC.
   The moment object __call__() method will accept a timezone to convert
   the internal UTC to a local time for display.
 * Tests for various combinations of inputs to the moment contructor
 * Tests for a range of timezones around the world

## 0.0.4 ... 2018.0208 22:25:57

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
