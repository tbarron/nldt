import numberize
import numbers
import pydoc
import pytest
import re
import tbx
import time
import nldt


# -----------------------------------------------------------------------------
def test_bug_001():
    """
    nldt.moment('2016-06-07')._yesterday() is yielding '2016-06-05' when it
    should be '2016-06-06'
    """
    pytest.debug_func()
    a = nldt.moment('2016-06-07')
    b = nldt.moment(a._yesterday())
    assert b() == '2016-06-06'


# -----------------------------------------------------------------------------
def test_repr():
    """
    The __repr__ method should provide enough info to rebuild the object
    """
    pytest.debug_func()
    c = nldt.moment()
    assert eval(repr(c)) == c


# -----------------------------------------------------------------------------
def test_notimezone():
    """
    Moments don't have timezones -- they are strictly UTC
    """
    pytest.debug_func()
    c = nldt.moment()
    with pytest.raises(AttributeError) as err:
        c.timezone()
    assert "object has no attribute 'timezone'" in str(err)


