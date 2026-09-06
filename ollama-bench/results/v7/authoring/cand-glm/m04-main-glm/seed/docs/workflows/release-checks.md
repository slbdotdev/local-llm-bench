# Release checks

*Read this before shipping. This is the only current description of the release-check
workflow; anything else in the tree that names a check command predates it.*

## What you have to work out first

Every stage's own document states a `declared_verified_on` date, in its Configuration table.
Every stage's own module states a `ROLLOUT_VERIFIED_ON` date. For nearly every stage the two
agree; a stage is **provisional** exactly when they disagree, and there is no shortcut past
comparing both dates for every stage -- the mismatch carries no marker of its own, and neither
value is repeated anywhere else in the tree.

A stage is excluded from the fixture only when it is provisional *and* its module's
`ROLLOUT_VERIFIED_ON` is dated on or after the cutover, `2034-04-01`. Being provisional by
itself does not exclude a stage, and a late rollout date by itself does not either (a stage
whose document and module agree is never provisional, however late the date is) -- both
conditions have to hold for the same stage. Neither `tools/build_fixture.py` nor
`tools/run_checks.py` will work this out for you: you have to read the stage documents and
modules yourself.

Write your findings to a small CSV, header `stage,rollout_date`, one row per stage you have
determined is provisional, with that stage's own module's effective rollout date. A stage you
do not list is treated as not provisional.

## The two commands, in order

    python tools/build_fixture.py <path-to-your-review-csv>
    python tools/run_checks.py

The first only combines your review with the manifest's stage list and applies the cutover
rule; it does not check your review against the tree, and it does not print which stage it
excluded or how many rows it wrote. The second is the actual check: it recomputes the correct
answer independently, from the real documents and modules, and compares it against whatever
`data/regression-fixture.csv` holds. It prints only `OK` or `FAIL`. If your review named the
wrong stage, or the right stage with the wrong date, the fixture it produces will not match,
and `tools/run_checks.py` will say so.

## What this replaces

`docs/operations.md`'s "Pre-release regression check (legacy)" section names
`python tools/legacy_check.py`. That module was removed when the fixture rework landed; the
section is stale and is kept only because nobody has gone back to delete it.
`tests/test_regression_checks.py` is the same vintage and fails on import for the same reason.
Neither is part of the current workflow. If a check command in this tree does not match the
two lines above, it is out of date.
