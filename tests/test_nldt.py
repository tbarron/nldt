"""
nldt - Natural Language Date/Time support
Copyright (c) 2017 - <the end of time>  Tom Barron
See file LICENSING for details

This file contains code for testing nldt functionality.
"""
from fixtures import fx_calls_debug    # noqa
# from fixtures import nl_oracle
# from tzlocal import get_localzone
# from datetime import datetime
# import numbers
# import os
import pytest
# import pytz
# from nldt.text import txt
import time
import nldt
# from nldt import moment as M

nldt.moment.default_tz('clear')


# -----------------------------------------------------------------------------
# @pytest.mark.parametrize("inp, exp", [
#     pytest.param(3.4, 3, id='numfloat'),
#     pytest.param(11, 11, id='numint'),
#     pytest.param(17, ValueError(txt['err-indxfy'].format(17)),
#                  id='year-range'),
#     pytest.param('5', 5, id='numstr'),
#     pytest.param('October', 10, id='str'),
#     pytest.param('oct', 10, id='abbr'),
#     ])
# def test_month_indexify(inp, exp):
#     """
#     Tests for month.indexify()
#     """
#     pytest.debug_func()
#     mon = nldt.month()
#     if isinstance(exp, Exception):
#         with pytest.raises(type(exp)):
#             assert mon.indexify(inp) == 'something'
#     else:
#         assert mon.indexify(inp) == exp


# -----------------------------------------------------------------------------
# def test_indexify_numfloat():
#     """
#     Cover lines in method month.indexify()
#     """
#     pytest.debug_func()
#     mon = nldt.month()
#     assert mon.indexify(3.4) == 3


# -----------------------------------------------------------------------------
# def test_indexify_numint():
#     """
#     Cover lines in method month.indexify()
#     """
#     pytest.debug_func()
#     mon = nldt.month()
#     assert mon.indexify(11) == 11
#     with pytest.raises(ValueError) as err:
#         assert mon.indexify(17) == -1
#     assert txt["err_indxfy"].format("17") in str(err)


# -----------------------------------------------------------------------------
# def test_indexify_numstr():
#     """
#     Cover lines in method month.indexify()
#     """
#     pytest.debug_func()
#     mon = nldt.month()
#     assert mon.indexify('5') == 5


# -----------------------------------------------------------------------------
# def test_indexify_str():
#     """
#     Cover lines in method month.indexify()
#     """
#     pytest.debug_func()
#     mon = nldt.month()
#     assert mon.indexify('October') == 10


# -----------------------------------------------------------------------------
# def test_indexify_lowstr():
#     """
#     Cover lines in method month.indexify()
#     """
#     pytest.debug_func()
#     mon = nldt.month()
#     assert mon.indexify('Oct') == 10


# -----------------------------------------------------------------------------
# def test_timezone():
#     """
#     Timezone should return the current timezone setting
#     """
#     pytest.debug_func()
#     if nldt.dst():
#         assert nldt.timezone() == time.tzname[1]
#     else:
#         assert nldt.timezone() == time.tzname[0]


# -----------------------------------------------------------------------------
# def test_match_monthnames():
#     """
#     Verify the regex returned by month.match_monthnames
#     """
#     pytest.debug_func()
#     m = nldt.month()
#     exp = "|".join(m.names())
#     exp = "(" + exp + ")"
#     assert exp == m.match_monthnames()


# -----------------------------------------------------------------------------
# @pytest.mark.parametrize("inp, exp", [
#     pytest.param(0, "monday", id='001'),
#     pytest.param("0", "monday", id='002'),
#     pytest.param("mon", "monday", id='003'),
#
#     pytest.param(1, "tuesday", id='004'),
#     pytest.param("1", "tuesday", id='005'),
#     pytest.param("tue", "tuesday", id='006'),
#
#     pytest.param(2, "wednesday", id='007'),
#     pytest.param("2", "wednesday", id='008'),
#     pytest.param("wed", "wednesday", id='009'),
#
#     pytest.param(3, "thursday", id='010'),
#     pytest.param("3", "thursday", id='011'),
#     pytest.param("thu", "thursday", id='012'),
#
#     pytest.param(4, "friday", id='013'),
#     pytest.param("4", "friday", id='014'),
#     pytest.param("fri", "friday", id='015'),
#
#     pytest.param(5, "saturday", id='016'),
#     pytest.param("5", "saturday", id='017'),
#     pytest.param("sat", "saturday", id='018'),
#
#     pytest.param(6, "sunday", id='019'),
#     pytest.param("6", "sunday", id='020'),
#     pytest.param("sun", "sunday", id='021'),
#
#     pytest.param(13, "except", id='022'),
#     pytest.param("13", "except", id='023'),
#     pytest.param("nosuch", "except", id='024'),
#     ])
# def test_week_fullname(inp, exp):
#     """
#     Test week.fullname
#     """
#     pytest.debug_func()
#     w = nldt.week()
#     if exp == "except":
#         with pytest.raises(ValueError) as err:
#             w.fullname(inp) == exp
#         assert txt["err-indxfy-f"].format(inp) in str(err)
#     else:
#         assert w.fullname(inp) == exp


# -----------------------------------------------------------------------------
# def test_week_day_number():
#     """
#     Test week.day_number()
#     """
#     pytest.debug_func()
#     w = nldt.week()
#     sat = nldt.moment("2000-01-01")
#     sun = nldt.moment("2000-01-02")
#
#     assert w.day_number(sat.epoch()) == 5        # payload
#     assert w.day_number(sat) == 5                # payload
#
#     with pytest.raises(TypeError) as err:
#         # payload
#         w.day_number(txt['xpr-tod']) == 14
#     assert txt["err-argmore"] in str(err)
#
#     assert w.day_number(sat, count='mon1') == 6    # payload
#     assert w.day_number(sun, count='mon1') == 7    # payload
#
#     assert w.day_number(sat, count='sun0') == 6    # payload
#     assert w.day_number(sun, count='sun0') == 0    # payload


# -----------------------------------------------------------------------------
# @pytest.mark.parametrize("tz, exp", [
#     pytest.param("Pacific/Norfolk", "XXX-11:00:00", id='Norfolk'),
#     pytest.param("Pacific/Pago_Pago", "SST11:00:00", id='Pago_Pago'),
#     pytest.param("Pacific/Marquesas", "XXX09:30:00", id='Marquesas'),
#     pytest.param("NZ-CHAT", "XXX-12:45:00XXX-13:45:00", id='NZ-CHAT'),
#     ])
# def test_tzstring(tz, exp):
#     """
#     tzstring for 'Pacific/Norfolk' should be 'XXX-11:30:00'
#     """
#     pytest.debug_func()
#     assert nldt.tzstring(tz) == exp


