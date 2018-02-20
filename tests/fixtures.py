import nldt
import pytest
import time
import tbx


# -----------------------------------------------------------------------------
def ftime(fmt, local=False, anchor=None):
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
    result = tbx.run("git --no-pager --sort=taggerdate tag")
    tag_l = result.strip().split("\n")
    latest_tag = tag_l[-1] if 0 < len(tag_l) else ""
    return latest_tag
