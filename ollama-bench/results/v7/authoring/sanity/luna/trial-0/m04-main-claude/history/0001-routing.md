# 0001 - routing: lower the entry limit

- Date: 2034-08-12
- Status: **superseded**
- Proposer: S. Nwachukwu (Delivery Engineering)

## Context

The routing stage refuses work above `limit`, currently 32. Capacity Planning asked whether
that number is a safety limit or a cost limit, because the two imply different responses
to a refusal: a safety limit means shed load, a cost limit means queue and bill.

## Decision

Recorded as a cost limit at the time. **Superseded** by the later ruling that the
routing stage sheds rather than queues; this entry is kept because the reasoning is
cited in two audits and removing it would break those references.

## Consequences

- `docs/routing.md` states the current behaviour and is authoritative over this entry.
- No change to `DEFAULT_ROUTING_LIMIT`.
- The Delivery Engineering team owns the shed-count dashboard.
