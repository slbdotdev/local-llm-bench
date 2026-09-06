# 0014 - tenancy: re-scope the cursor limit

- Date: 2035-03-20
- Status: **accepted**
- Proposer: K. Sorensen (Delivery Engineering)

## Context

The tenancy stage refuses work above `limit`, currently 24. Capacity Planning asked whether
that number is a safety limit or a cost limit, because the two imply different responses
to a refusal: a safety limit means shed load, a cost limit means queue and bill.

## Decision

It is a **safety limit**. The tenancy stage sheds rather than queues, and `backfill` is
responsible for reporting the shed count. The number itself is unchanged at 24.

## Consequences

- `docs/tenancy.md` states the current behaviour and is authoritative over this entry.
- No change to `DEFAULT_TENANCY_LIMIT`.
- The Delivery Engineering team owns the shed-count dashboard.

## Repair-allowance bands

Every change to this stage's repair-allowance bands since it was commissioned,
oldest first. The bands themselves and their sizes are in `src/kelvin/tenancy_core.py`; this
entry records only what has happened to them, and `docs/policy/guarantees.md` says how to
read the two together. The consequence above about `docs/tenancy.md` is this entry's
ruling on `limit` and decides nothing about the bands below.

- No band has been stood down or taken back up since this stage was
  commissioned.
