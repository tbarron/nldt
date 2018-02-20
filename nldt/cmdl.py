"""
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
    fmt = opts['--format']
    zone = opts['--zone']
    prs = nldt.Parser()
    when = nldt.moment(opts['--when'])
    if expr in ['today', 'tomorrow']:
        ref = prs(expr, start=when)
        print(ref(fmt, tz=zone))
