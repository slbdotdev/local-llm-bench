# 0013 - quota: re-scope the marker limit

- Date: 2034-08-09
- Status: **accepted**
- Proposer: N. Oyelaran (Capacity Planning)

## Context

The quota stage refuses work above `limit`, currently 48. Capacity Planning asked whether
that number is a safety limit or a cost limit, because the two imply different responses
to a refusal: a safety limit means shed load, a cost limit means queue and bill.

## Decision

It is a **safety limit**. The quota stage sheds rather than queues, and `backfill` is
responsible for reporting the shed count. The number itself is unchanged at 48.

## Consequences

- `docs/quota.md` states the current behaviour and is authoritative over this entry.
- No change to `DEFAULT_QUOTA_LIMIT`.
- The Capacity Planning team owns the shed-count dashboard.

## Repair-allowance bands

Every change to this stage's repair-allowance bands since it was commissioned,
oldest first. The bands themselves and their sizes are in `src/kelvin/quota_gate.py`; this
entry records only what has happened to them, and `docs/policy/guarantees.md` says how to
read the two together. The consequence above about `docs/quota.md` is this entry's
ruling on `limit` and decides nothing about the bands below.

- 2034-02-11 - `bulk-repair` **stood down**. The class was merged into general repair
  traffic at the request of the on-call team.
- 2035-07-09 - `bulk-repair` **restored**. The recovery service missed its own window twice
  in one quarter.
