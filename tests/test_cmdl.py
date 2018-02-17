import nldt
from fixtures import ftime
import pytest
import tbx
import time


# -----------------------------------------------------------------------------
@pytest.mark.parametrize("cmd, exp", [
    ('nldt today', ftime('%Y-%m-%d')),

    ('nldt -z local today', ftime('%Y-%m-%d', local=True)),

    ('nldt -w "2000.1231 09:07:43" today', '2000-12-31'),

    ('nldt -z local -f "%Y.%m%d %H:%M" today', ftime('%Y.%m%d %H:%M', True)),

    ('nldt -f "%Y.%m%d %H:%M" today', ftime('%Y.%m%d %H:%M')),

    ('nldt -z local -w "2000.1231 09:07:43" today', '2000-12-31'),

    ('nldt -f "%Y.%m%d %H:%M:%S" -w 978253663 today',
     '2000.1231 09:07:43'),

    ('nldt -z local -f "%Y.%m%d %H:%M:%S" -w 978275263 today',
     '2000.1231 10:07:43'),
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
