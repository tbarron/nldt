import pytest
import tbx


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
    result = tbx.run("git --no-pager tag")
    tag_l = result.strip().split("\n")
    latest_tag = tag_l[-1] if 0 < len(tag_l) else ""
    return latest_tag

