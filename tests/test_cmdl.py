from fixtures import fx_calls_debug      # noqa
from fixtures import ftime
import pexpect
import pytest
import tbx
import time


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

    ('nldt tomorrow', ftime("%Y-%m-%d", anchor=time.time()+24*3600)),
    ])
def test_cmdline(cmd, exp):
    """
    Test nldt on the command line
    LOC ANC FMT
     0   0   0     nldt    today
     0   0   1     nldt -f '%c' today
     0   1   0     nldt -w '2005.0302' today
     0   1   1     nldt -w '2005.0302' -f '%c' today
     1   0   0     nldt -L today
     1   0   1     nldt -L -f '%c' today
     1   1   0     nldt -L -w '2006.0420' today
     1   1   1     nldt -L -w '2006.0420' -f '%c' today
    """
    pytest.debug_func()
    result = tbx.run(cmd)
    assert result.strip() == exp


# -----------------------------------------------------------------------------
def test_debug():
    """
    Cover the line where we fire up the debugger
    """
    proc = pexpect.spawn('nldt -d today')
    proc.expect('(Pdb)')
    proc.sendline('c')
    proc.expect(pexpect.EOF)
