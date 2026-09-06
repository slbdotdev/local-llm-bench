# 0005 - rollup: lower the segment limit

- Date: 2035-12-02
- Status: **accepted**
- Proposer: K. Sorensen (Delivery Engineering)

## Context

The rollup stage refuses work above `limit`, currently 12. Capacity Planning asked whether
that number is a safety limit or a cost limit, because the two imply different responses
to a refusal: a safety limit means shed load, a cost limit means queue and bill.

## Decision

It is a **safety limit**. The rollup stage sheds rather than queues, and `reconcile` is
responsible for reporting the shed count. The number itself is unchanged at 12.

## Consequences

- `docs/rollup.md` states the current behaviour and is authoritative over this entry.
- No change to `DEFAULT_ROLLUP_LIMIT`.
- The Delivery Engineering team owns the shed-count dashboard.

Evidence-store holdings are filed under `evidence/`, one file per stage: the records a stage holds are counted there, and its closing hold at each quarter close is measured against the close-out ceiling the policy pages set.
