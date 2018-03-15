from nldt import moment as M
import nldt
import os
import pytest
from nldt.text import txt


# -----------------------------------------------------------------------------
def test_bug_pctsec():
    """
    given
        x = moment()
    x.epoch() should be equal to int(x('%s'))

    The bug was that the epoch value was being stored and reported as a float,
    which was causing int to throw a ValueError.
    """
    pytest.debug_func()
    now = nldt.moment()
    assert now.epoch() == int(now("%s"))


# -----------------------------------------------------------------------------
def test_tz_context_keyerr():
    """
    Test for 'with nldt.tz_context(ZONE)' when 'TZ' is not in os.environ (so
    pre-fix, 'del os.environ['TZ']' throws a KeyError)
    """
    pytest.debug_func()
    tzorig = None
    if 'TZ' in os.environ:
        tzorig = os.getenv('TZ')

    with nldt.tz_context('US/Pacific'):
        then = M(txt['date02'], itz='US/Pacific')
        assert then("%F %T", otz='US/Pacific') == txt['date02']

    if tzorig:
        os.environ['TZ'] = tzorig
    elif 'TZ' in os.environ:
        del os.environ['TZ']
