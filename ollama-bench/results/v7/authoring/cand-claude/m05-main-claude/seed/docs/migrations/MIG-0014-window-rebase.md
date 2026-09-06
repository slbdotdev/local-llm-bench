# MIG-0014 - window rebase

- Status: **in force**

A subset of stages were rebased onto a new enforced-window baseline as part of the
retention overhaul. A rebased stage's component document intentionally still
states its pre-rebase `enforced_window_s`, kept as a historical record of the number an
operator was told before the rebase; it is not expected to equal the module and is
not covered by DR-0091's comparison.

The current list of rebased stages changes with each wave and is kept where the
test suite exercises it on every change, rather than in this note, which would go
stale between waves: see `tests/test_window_migration_coverage.py`.

This note does not restate DR-0091's rule; a stage not named by that test is fully
in scope for it.
