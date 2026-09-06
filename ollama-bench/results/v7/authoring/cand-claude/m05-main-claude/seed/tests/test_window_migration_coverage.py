"""Confirms which stages are currently exempt from the DR-0091 enforced-window comparison.

See docs/migrations/MIG-0014-window-rebase.md for why this list exists and is kept here rather than in the
migration note itself. A stage named here is exempt: its component document intentionally
still shows the pre-rebase `enforced_window_s` and is not expected to equal the module.
"""

MIGRATED_STAGES = [
    'audit',
    'backfill',
    'digest',
    'ledger',
    'reconcile',
]


def test_migration_coverage_matches_the_wave_count():
    assert len(MIGRATED_STAGES) == 5
