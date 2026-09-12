# 0003 - dispatch: lower the batch limit

- Date: 2033-10-07
- Status: **superseded**
- Proposer: N. Oyelaran (Delivery Engineering)

## Context

The dispatch stage refuses work above `limit`, currently 960. Capacity Planning asked whether
that number is a safety limit or a cost limit, because the two imply different responses
to a refusal: a safety limit means shed load, a cost limit means queue and bill.

## Decision

Recorded as a cost limit at the time. **Superseded** by the later ruling that the
dispatch stage sheds rather than queues; this entry is kept because the reasoning is
cited in two audits and removing it would break those references.

## Consequences

- `docs/dispatch.md` states the current behaviour and is authoritative over this entry.
- No change to `DEFAULT_DISPATCH_LIMIT`.
- The Delivery Engineering team owns the shed-count dashboard.
