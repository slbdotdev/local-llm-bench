# 0002 - backfill: re-scope the slot limit

- Date: 2035-03-23
- Status: **superseded**
- Proposer: A. Villanueva (Capacity Planning)

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
- The Capacity Planning team owns the shed-count dashboard.

@C affirm
