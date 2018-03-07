"""
nldt - Natural Language Date/Time support
Copyright (c) 2017 - <the end of time>  Tom Barron
See file LICENSING for details

This file contains code for testing nldt functionality.
"""
import nldt
import pytest
import time
import tbx


# -----------------------------------------------------------------------------
def local_formatted(fmt, epoch=None, dstor=None):
    """
    Format the epoch time as local
    """
    dstor = dstor or time.localtime
    return time.strftime(fmt, dstor(epoch))


# -----------------------------------------------------------------------------
def ftime(fmt, local=True, anchor=None):
    """
    Provide an oracle for test_cmdline
    """
    point = nldt.moment(anchor)
    if local:
        tm = time.localtime(point.epoch())
    else:
        tm = time.gmtime(point.epoch())
    rval = time.strftime(fmt, tm)
    return rval


# -----------------------------------------------------------------------------
@pytest.fixture(autouse=True)
def fx_calls_debug(request):
    """
    This fixture fails if the target test does not call pytest.debug_func()
    """
    if 'debug_func' not in request.function.__code__.co_names:
        pytest.fail("Test '{}' does not call pytest.debug_func"
                    "".format(request.function.__code__.co_name))


# -----------------------------------------------------------------------------
@pytest.fixture
def fx_git_last_tag():
    """
    Determine and return the latest git tag
    """
    result = tbx.run("git --no-pager tag --sort=taggerdate")
    tag_l = result.strip().split("\n")
    latest_tag = tag_l[-1] if 0 < len(tag_l) else ""
    return latest_tag
