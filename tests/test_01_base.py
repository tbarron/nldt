"""
nldt - Natural Language Date/Time support
Copyright (c) 2017 - <the end of time>  Tom Barron
See file LICENSING for details

This file contains code for testing nldt functionality.
"""
import nldt
import pytest


# -----------------------------------------------------------------------------
@pytest.mark.parametrize("inp, exp", [
    pytest.param(35, True, id='int'),
    pytest.param(-19, True, id='negint'),
    pytest.param(35.7, True, id='float'),
    pytest.param(-74.392, True, id='negfloat'),
    pytest.param('ABC', False, id='notint'),
    pytest.param('17abc', False, id='hasalpha'),
    pytest.param('92', True, id='strint'),
    pytest.param('-13', True, id='str negint'),
    pytest.param('-13.9', True, id='str negfloat'),
    pytest.param('13.9', True, id='str float'),
    ])
def test_isnum(inp, exp):
    """
    Verify that nldt.isnum() behaves as expected
    """
    pytest.debug_func()
    assert nldt.isnum(inp) == exp


# -----------------------------------------------------------------------------
@pytest.mark.parametrize("tz, exp", [
    ("US/Eastern", {'std': {'name': 'EST', 'secs': -18000},
                    'dst': {'name': 'EDT', 'secs': -14400}
                    }),
    ("Pacific/Pago_Pago", {'std': {'name': 'SST', 'secs': -39600}}),
    ("Pacific/Marquesas", {'std': {'name': '-0930', 'secs': -34200}}),
    ("NZ-CHAT", {'std': {'name': '+1245', 'secs': 45900},
                 'dst': {'name': '+1345', 'secs': 49500}}),
    ])
def test_offset_list(tz, exp):
    """
    Check the behavior of function offset_list()
    """
    pytest.debug_func()
    result = nldt.offset_list(tz)
    assert result == exp
