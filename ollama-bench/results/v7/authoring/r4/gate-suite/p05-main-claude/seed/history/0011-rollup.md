# 0011 - rollup: raise the batch limit

- Date: 2035-06-14
- Status: **accepted**
- Proposer: C. Batbayar (Data Stewardship)

## Context

The rollup stage refuses work above `limit`, currently 64. Capacity Planning asked whether
that number is a safety limit or a cost limit, because the two imply different responses
to a refusal: a safety limit means shed load, a cost limit means queue and bill.

## Decision

It is a **safety limit**. The rollup stage sheds rather than queues, and `backfill` is
responsible for reporting the shed count. The number itself is unchanged at 64.

## Consequences

- `docs/rollup.md` states the current behaviour and is authoritative over this entry.
- No change to `DEFAULT_ROLLUP_LIMIT`.
- The Data Stewardship team owns the shed-count dashboard.

## Repair-allowance bands

Every change to this stage's repair-allowance bands since it was commissioned,
oldest first. The bands themselves and their sizes are in `src/kelvin/rollup_view.py`; this
entry records only what has happened to them, and `docs/policy/guarantees.md` says how to
read the two together. The consequence above about `docs/rollup.md` is this entry's
ruling on `limit` and decides nothing about the bands below.

- 2034-12-24 - `bulk-repair` **withdrawn**. The work was folded into the nightly sweep,
  which has no per-stage guarantee.
- 2035-05-14 - `bulk-repair` **taken back up**. The migration finished and the reserved
  records were returned.
