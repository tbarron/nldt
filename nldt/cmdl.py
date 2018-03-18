"""
nldt - Natural Language Date/Time support
Copyright (c) 2017 - <the end of time>  Tom Barron
See file LICENSING for details

This file contains code for testing nldt functionality.
-------------------------------------------------------------------------------

Usage:
    nldt [-d] [-f=<fmt>] [-w=<anchor>] [-z=<timezone>] [DATE_TIME_EXPR ...]

Options:
    -d, --debug            run the debugger
    -f, --format=<fmt>     strftime-style output format
    -w, --when=<anchor>    define 'now'
    -z, --zone=<timezone>  'local' or explicit timezone

<anchor> can be

Examples:
    $ nldt now
    2018-02-16 11:49:13
    $ nldt today
    2018-02-16
    $ nldt tomorrow
    2018-02-17
    $ nldt -w '2018-01-01' yesterday
    2017-12-31
"""
import docopt
import nldt
import pdb
# import sys


# -----------------------------------------------------------------------------
def main():
    """
    Here is where we start
    """
    opts = docopt.docopt(__doc__)
    if opts['--debug']:
        pdb.set_trace()

    expr = " ".join(opts['DATE_TIME_EXPR']) or 'now'
    fmt = opts['--format'] if opts['--format'] else default_format(expr)
    zone = opts['--zone'] if opts['--zone'] else default_zone(expr)

    prs = nldt.Parser()
    when = nldt.moment(opts['--when'])
    ref = prs(expr, start=when)

    print(ref(**{'fmt': fmt, 'otz': zone}))


# -----------------------------------------------------------------------------
def big_unit(expr):
    """
    Return True if *expr* is based on a 'big' unit (day or larger), otherwise
    False.
    """
    big_units = ['day', 'week', 'month', 'year', 'morrow']
    return any([x in expr for x in big_units])


# -----------------------------------------------------------------------------
def default_format(expr):
    """
    Select a default display format for this *expr*
    """
    if big_unit(expr):
        rval = "%F"
    else:
        rval = "%F %T"
    return rval


# -----------------------------------------------------------------------------
def default_zone(expr):
    """
    Select a display zone that will work best for this *expr*
    """
    if big_unit(expr):
        rval = 'utc'
    else:
        rval = 'local'
    return rval
