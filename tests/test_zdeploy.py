from fixtures import fx_calls_debug    # noqa
from fixtures import fx_git_last_tag
import nldt
import pytest
import re
import tbx


# -----------------------------------------------------------------------------
def test_deployable(fx_git_last_tag):
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

    # determine the current branch
    result = tbx.run("git branch")
    for candy in result.split("\n"):
        if '*' in candy:
            curb = candy.split()[1]
            break

    # If the current branch is not 'master', the only requirement for pushing
    # is that everything be committed.
    if curb != 'master':
        return True

    # If the current branch is 'master', the version and latest tag must match
    # and the latest tag must point at HEAD for the project to be deployable
    # (i.e., releasable, since a push on master IS a release!)

    # check the current version against the most recent tag
    assert fx_git_last_tag == nldt.version(), "Version does not match tag"

    # verify that the most recent tag points at HEAD
    cmd = "git --no-pager log -1 --format=format:\"%H\""
    tag_hash = tbx.run(cmd + " {}".format(latest_tag))
    head_hash = tbx.run(cmd)
    assert head_hash == tag_hash, "Tag != HEAD"
