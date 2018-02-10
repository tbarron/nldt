import pytest


# -----------------------------------------------------------------------------
@pytest.fixture(autouse=True)
def fx_calls_debug(request):
    if 'debug_func' not in request.function.__code__.co_names:
        pytest.fail("Test '{}' does not call pytest.debug_func"
                    "".format(request.function.__code__.co_name))


