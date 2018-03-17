"""
nldt - Natural Language Date/Time support
Copyright (c) 2017 - <the end of time>  Tom Barron
See file LICENSING for details

This file contains code for testing nldt functionality.
"""
from fixtures import fx_calls_debug    # noqa
import nldt
from nldt import moment
from nldt import duration
import pytest
from nldt.text import txt
import time

moment.default_tz('utc')


