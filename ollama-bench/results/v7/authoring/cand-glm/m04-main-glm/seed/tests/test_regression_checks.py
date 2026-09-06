"""Superseded -- kept for historical reference only.

This predates the fixture rework and checks the old, fixed fixture path directly. It is not
part of the current release checks; see `docs/workflows/release-checks.md` for those. Running
this file will fail on import, because `tools/legacy_check` was removed when the fixture
rework landed.
"""
from tools import legacy_check  # noqa: F401  (removed; this module predates the rework)


def test_fixture_has_the_old_fixed_row_count():
    rows = legacy_check.load_fixture("data/fixture.csv")
    assert len(rows) == 21
