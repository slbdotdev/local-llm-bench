# 0000 - backfill: raise the entry limit

- Date: 2033-01-01
- Status: **superseded**
- Proposer: C. Batbayar (Client Integrations)

## Context

The backfill stage refuses work above `limit`, currently 24. Capacity Planning asked whether
that number is a safety limit or a cost limit, because the two imply different responses
to a refusal: a safety limit means shed load, a cost limit means queue and bill.

## Decision

Recorded as a cost limit at the time. **Superseded** by the later ruling that the
backfill stage sheds rather than queues; this entry is kept because the reasoning is
cited in two audits and removing it would break those references.

## Consequences

- `docs/backfill.md` states the current behaviour and is authoritative over this entry.
- No change to `DEFAULT_BACKFILL_LIMIT`.
- The Client Integrations team owns the shed-count dashboard.

## Repair-allowance bands

Every change to this stage's repair-allowance bands since it was commissioned,
oldest first. The bands themselves and their sizes are in `src/kelvin/backfill_gate.py`; this
entry records only what has happened to them, and `docs/policy/guarantees.md` says how to
read the two together. The consequence above about `docs/backfill.md` is this entry's
ruling on `limit` and decides nothing about the bands below.

- 2034-01-01 - `bulk-repair` **retired**. The rewind path moved to the recovery service and
  the guarantee moved with it.
