from fixtures import fx_calls_debug
import nldt


def test_hhmm():
    """
    Verify that nldt.hhmm() correctly converts seconds into HHMM
    """
    assert nldt.hhmm(-18000) == '-0500'
    assert nldt.hhmm(18000) == '0500'
    assert nldt.hhmm(7200) == '0200'
