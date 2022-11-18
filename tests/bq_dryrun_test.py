from __future__ import annotations

from bq_pre_commit_hooks.bq_dryrun import main
from testing.util import get_resource_path


def test_failing_file():
    ret = main([get_resource_path('fail_test.sql')])
    assert ret == 1


def test_passing_file():
    ret = main([get_resource_path('pass_test.sql')])
    assert ret == 0
