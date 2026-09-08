# Capacity exceptions

*What the project means by the phrase, and how a quarterly report is assembled from
it. This document defines the term; it does not decide which policy governs the
report this quarter — that is settled separately, by whichever ruling on the subject
is currently in force.*

## Definition

A stage is a **capacity exception** exactly when its component document's declared
`review_stamp` (the `docs/<stage>.md` configuration table) differs from the effective
`review_stamp` its own module actually confirms, `DEFAULT_<STAGE>_REVIEW_STAMP`. A
mismatch in `limit` or `window_s` is not a capacity exception — both are unrelated,
pipeline-level numbers, and every stage's document and module already agree on both;
the manifest's human-readable `note` is advisory and is not the criterion.

The `limit` a stage's own module enforces, `DEFAULT_<STAGE>_LIMIT`, is what
'effective limit' means everywhere in this document and in any report drawn from it;
the word is never used for `window_s` or for `review_stamp`.

## Reporting

Not every capacity exception is reported. The capacity audit log
(`data/capacity-audit-log.csv`) records a `disposition` for every stage; a
disposition of `tracked-elsewhere` means another review already owns that stage's
exception and it is not reported here, but a disposition is only authoritative under
a policy currently in force that grants it that effect. The general, numbered pages
under `docs/policy/` cover retention, evidence, access and change; none of them
addresses capacity exceptions. The ruling that does is filed separately, and it is
the only one to apply — a superseded or retired ruling on the same subject is not.

## What is not a finding

- A `review_stamp` divergence exempted by a disposition currently in force. It
  remains a capacity exception for bookkeeping; it is simply not on this quarter's
  report.
- Any earlier compilation of this report. A compilation is only as current as the
  audit log and the policy it was made against, and neither stands still.
