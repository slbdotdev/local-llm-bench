# 0002 - reconcile: raise the bundle limit

- Date: 2035-03-23
- Status: **superseded**
- Proposer: N. Oyelaran (Capacity Planning)

## Context

The reconcile stage refuses work above `limit`, currently 480. Capacity Planning asked whether
that number is a safety limit or a cost limit, because the two imply different responses
to a refusal: a safety limit means shed load, a cost limit means queue and bill.

## Decision

Recorded as a cost limit at the time. **Superseded** by the later ruling that the
reconcile stage sheds rather than queues; this entry is kept because the reasoning is
cited in two audits and removing it would break those references.

## Consequences

- `docs/reconcile.md` states the current behaviour and is authoritative over this entry.
- No change to `DEFAULT_RECONCILE_LIMIT`.
- The Capacity Planning team owns the shed-count dashboard.
