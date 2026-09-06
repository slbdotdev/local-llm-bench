# 0006 - drain: raise the segment limit

- Date: 2033-07-13
- Status: **accepted**
- Proposer: P. Ravindran (Delivery Engineering)

## Context

The drain stage refuses work above `limit`, currently 12. Capacity Planning asked whether
that number is a safety limit or a cost limit, because the two imply different responses
to a refusal: a safety limit means shed load, a cost limit means queue and bill.

## Decision

It is a **safety limit**. The drain stage sheds rather than queues, and `backfill` is
responsible for reporting the shed count. The number itself is unchanged at 12.

## Consequences

- `docs/drain.md` states the current behaviour and is authoritative over this entry.
- No change to `DEFAULT_DRAIN_LIMIT`.
- The Delivery Engineering team owns the shed-count dashboard.

## Repair-allowance bands

Every change to this stage's repair-allowance bands since it was commissioned,
oldest first. The bands themselves and their sizes are in `src/kelvin/drain_store.py`; this
entry records only what has happened to them, and `docs/policy/guarantees.md` says how to
read the two together. The consequence above about `docs/drain.md` is this entry's
ruling on `limit` and decides nothing about the bands below.

- 2034-07-16 - `partial-batch` **handed back**. The reserved records were needed for a
  migration and were never handed back.
