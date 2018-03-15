import nldt
import pytest


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


