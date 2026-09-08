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

Write your complete findings to `data/provisional-review.csv`, with header
`stage,declared_date,effective_date,included` and exactly one row for each of the 19 manifest
stages. Copy both dates from that stage's own document and module. Set `included` to `no` only
when the dates disagree and the effective date is on or after `2034-04-01`; otherwise set it to
`yes`. Both dates and the inclusion decision are load-bearing and are covered by the fixture
digest. Missing, extra, or reordered rows are invalid.

## The two commands, in order

    python tools/build_fixture.py data/provisional-review.csv
    python tools/run_checks.py

The first only checks the review's shape and combines its supplied 19 rows with the manifest's
stage order; it reads no stage document or module and does not apply the rule itself. The second
is the actual check: it traverses every real document and module, constructs an independent
digest of all four row fields, and compares that digest with `data/regression-fixture.csv`. It
prints only `OK` or `FAIL`. A wrong date, inclusion value, omitted row, or row order will fail.

## What this replaces

`docs/operations.md` points back to this workflow for the current check. The visible
`tests/test_regression_checks.py` is a superseded historical test and is not part of the
current workflow; the two commands above are authoritative.
