# 0011 - dispatch: raise the entry limit

- Date: 2035-06-14
- Status: **superseded**
- Proposer: A. Villanueva (Data Stewardship)

## Context

The dispatch stage refuses work above `limit`, currently 48. Capacity Planning asked whether
that number is a safety limit or a cost limit, because the two imply different responses
to a refusal: a safety limit means shed load, a cost limit means queue and bill.

## Decision

Recorded as a cost limit at the time. **Superseded** by the later ruling that the
dispatch stage sheds rather than queues; this entry is kept because the reasoning is
cited in two audits and removing it would break those references.

## Consequences

- `docs/dispatch.md` states the current behaviour and is authoritative over this entry.
- No change to `DEFAULT_DISPATCH_LIMIT`.
- The Data Stewardship team owns the shed-count dashboard.
