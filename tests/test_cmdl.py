"""
nldt - Natural Language Date/Time support
Copyright (c) 2017 - <the end of time>  Tom Barron
See file LICENSING for details

This file contains code for testing nldt functionality.
"""
from fixtures import fx_calls_debug      # noqa
from fixtures import ftime
import pexpect
import pytest
import tbx
import time


# -----------------------------------------------------------------------------
def test_now_nofmt_nozone():
    """
    'nldt now' (no zone, no format) should produce the current UTC time in
    default format (ISO).
    """
    pytest.debug_func()
    # payload
    result = tbx.run('nldt now')
    assert result.strip() == time.strftime("%F %T", time.gmtime())


# -----------------------------------------------------------------------------
def test_now_nofmt_zone():
    """
    'nldt -z local now' (with zone local, no format) should produce the current
    local time in default format (ISO).
    """
    pytest.debug_func()
    # payload
    result = tbx.run('nldt now -z local')
    assert result.strip() == time.strftime("%F %T")


# -----------------------------------------------------------------------------
def test_unanchored_now():
    """
    'nldt now' should give the current UTC time. By including %s in the output
    format, we can get the time index to verify against.
    """
    pytest.debug_func()
    # payload
    result = tbx.run('nldt now -f "%s %F %T"')
    epoch, ymd = result.split(" ", 1)
    epoch = int(epoch)
    now = time.time()
    assert abs(int(now) - epoch) < 2
    assert ymd.strip() == time.strftime("%F %T", time.gmtime(epoch))


# -----------------------------------------------------------------------------
def test_unanchored_noarg():
    """
    'nldt' with no arguments should behave like 'nldt now' (like dt(1)). We do
    set the format (-f '...') but provide no date/time expression
    """
    pytest.debug_func()
    # payload
    result = tbx.run('nldt -f "%s %F %T"')
    epoch, ymd = result.split(" ", 1)
    epoch = int(epoch)
    now = time.time()
    assert abs(int(now) - epoch) < 2
    assert ymd.strip() == time.strftime("%F %T", time.gmtime(epoch))


# -----------------------------------------------------------------------------
@pytest.mark.parametrize("cmd, exp", [
    # today
    ('nldt today', ftime('%Y-%m-%d')),

    ('nldt -z local today', ftime('%Y-%m-%d', local=True)),

    ('nldt -w "2000.1231 09:07:43" today', '2000-12-31'),

    ('nldt -z local -f "%Y.%m%d %H" today', ftime('%Y.%m%d %H', True)),

    ('nldt -f "%Y.%m%d %H" today', ftime('%Y.%m%d %H')),

    ('nldt -z local -w "2000.1231 09:07:43" today',
     ftime('%Y-%m-%d', local=True, anchor='2000.1231 09:07:43')),

    ('nldt -f "%Y.%m%d %H:%M:%S" -w 978253663 today',
     '2000.1231 09:07:43'),

    ('nldt -z local -f "%Y.%m%d %H:%M:%S" -w 978275263 today',
     ftime('%Y.%m%d %H:%M:%S', local=True, anchor='2000.1231 15:07:43')),

    ('nldt -z US/Pacific -f "%Y.%m%d %H:%M:%S" -w 978275263 today',
     '2000.1231 07:07:43'),

    # tomorrow
    ('nldt tomorrow', ftime("%Y-%m-%d", anchor=time.time()+24*3600)),

    ('nldt -z local tomorrow',
     ftime('%Y-%m-%d', local=True, anchor=time.time()+24*3600)),

    ('nldt -w "2000.1231 09:07:43" tomorrow', '2001-01-01'),

    ('nldt -z local -f "%Y.%m%d %H" tomorrow',
     ftime('%Y.%m%d %H', True, anchor=time.time()+24*3600)),

    ('nldt -f "%Y.%m%d %H" tomorrow',
     ftime('%Y.%m%d %H', anchor=time.time()+24*3600)),

    ('nldt -z local -w "2000.1231 09:07:43" tomorrow',
     ftime('%Y-%m-%d', local=True, anchor='2001.0101 09:07:43')),

    ('nldt -f "%Y.%m%d %H:%M:%S" -w 978253663 tomorrow',
     '2001.0101 09:07:43'),

    ('nldt -z local -f "%Y.%m%d %H:%M:%S" -w 978275263 tomorrow',
     ftime('%Y.%m%d %H:%M:%S', local=True, anchor='2001.0101 15:07:43')),

    ('nldt -z US/Pacific -f "%Y.%m%d %H:%M:%S" -w 978275263 tomorrow',
     '2001.0101 07:07:43'),

    # yesterday
    ('nldt yesterday', ftime("%Y-%m-%d", anchor=time.time()-24*3600)),

    ('nldt -z local yesterday',
     ftime('%Y-%m-%d', local=True, anchor=time.time()-24*3600)),

    ('nldt -w "2000.1231 09:07:43" yesterday', '2000-12-30'),

    ('nldt -z local -f "%Y.%m%d %H" yesterday',
     ftime('%Y.%m%d %H', True, anchor=time.time()-24*3600)),

    ('nldt -f "%Y.%m%d %H" yesterday',
     ftime('%Y.%m%d %H', anchor=time.time()-24*3600)),

    ('nldt -z local -w "2000.1231 09:07:43" yesterday',
     ftime('%Y-%m-%d', local=True, anchor='2000.1230 09:07:43')),

    ('nldt -f "%Y.%m%d %H:%M:%S" -w 978253663 yesterday',
     '2000.1230 09:07:43'),

    ('nldt -z local -f "%Y.%m%d %H:%M:%S" -w 978275263 yesterday',
     ftime('%Y.%m%d %H:%M:%S', local=True, anchor='2000.1230 15:07:43')),

    ('nldt -z US/Pacific -f "%Y.%m%d %H:%M:%S" -w 978275263 yesterday',
     '2000.1230 07:07:43'),

    ])
def test_cmdline(cmd, exp):
    """
    Test nldt on the command line

    Note that the unanchored tests (i.e., those with no -w/--when on the nldt
    command) are liable to fail if the test suite is run within 15 seconds or
    so of the change of an hour. If this is a problem, reduce the resolution to
    the day level. This risk cannot be completely eliminated without anchoring
    the time reference, which would defeat the purpose of these tests.
    """
    pytest.debug_func()
    result = tbx.run(cmd)
    assert result.strip() == exp


# -----------------------------------------------------------------------------
def test_debug():
    """
    Cover the line where we fire up the debugger
    """
    pytest.debug_func()
    proc = pexpect.spawn('nldt -d today')
    proc.expect('(Pdb)')
    proc.sendline('c')
    proc.expect(pexpect.EOF)
