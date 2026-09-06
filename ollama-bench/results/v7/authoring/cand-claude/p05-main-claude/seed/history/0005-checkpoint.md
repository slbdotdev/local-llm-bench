# 0005 - checkpoint: lower the segment limit

- Date: 2035-12-02
- Status: **accepted**
- Proposer: H. Bergstrom (Delivery Engineering)

## Context

The checkpoint stage refuses work above `limit`, currently 24. Capacity Planning asked whether
that number is a safety limit or a cost limit, because the two imply different responses
to a refusal: a safety limit means shed load, a cost limit means queue and bill.

## Decision

It is a **safety limit**. The checkpoint stage sheds rather than queues, and `backfill` is
responsible for reporting the shed count. The number itself is unchanged at 24.

## Consequences

- `docs/checkpoint.md` states the current behaviour and is authoritative over this entry.
- No change to `DEFAULT_CHECKPOINT_LIMIT`.
- The Delivery Engineering team owns the shed-count dashboard.

## Repair-allowance bands

Every change to this stage's repair-allowance bands since it was commissioned,
oldest first. The bands themselves and their sizes are in `src/kelvin/checkpoint_gate.py`; this
entry records only what has happened to them, and `docs/policy/guarantees.md` says how to
read the two together. The consequence above about `docs/checkpoint.md` is this entry's
ruling on `limit` and decides nothing about the bands below.

- 2034-06-09 - `evidence-refill` **stood down**. The class was merged into general repair
  traffic at the request of the on-call team.
