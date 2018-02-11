from fixtures import fx_calls_debug    # noqa
import pytest
import re
import tbx
from version import _version


# -----------------------------------------------------------------------------
def test_deployable():
    """
    Check version against last git tag and check for untracked files or
    outstanding updates.
    """
    pytest.debug_func()
    result = tbx.run("git status --porc")

    # check for untracked files
    msg = "There are untracked files"
    assert "??" not in result, msg

    # check for unstaged updates or staged but uncommitted updates
    msg = "There are uncommitted updates, staged or unstaged"
    assert not re.findall("\n?(MM|MA|AM|AA|A |M | A| M)", result), msg

    # check the current version against the most recent tag
    result = tbx.run("git --no-pager tag")
    tag_l = result.strip().split("\n")
    if 0 < len(tag_l):
        latest_tag = tag_l[-1]
    else:
        latest_tag = ""

    assert latest_tag == _version, "Version does not match tag"

    # verify that the most recent tag points at HEAD
    cmd = "git --no-pager log -1 --format=format:\"%H\""
    tag_hash = tbx.run(cmd + " {}".format(latest_tag))
    head_hash = tbx.run(cmd)
    assert head_hash == tag_hash, "Tag != HEAD"
