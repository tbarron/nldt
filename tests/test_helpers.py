from fixtures import fx_calls_debug     # noqa
import nldt
import pytest


def test_hhmm():
    """
    Verify that nldt.hhmm() correctly converts seconds into HHMM
    """
    pytest.debug_func()
    assert nldt.hhmm(-18000) == '-0500'
    assert nldt.hhmm(18000) == '0500'
    assert nldt.hhmm(7200) == '0200'
