# 0015 - routing: clarify the token limit

- Date: 2033-10-04
- Status: **superseded**
- Proposer: T. Abarca (Delivery Engineering)

## Context

The routing stage refuses work above `limit`, currently 12. Capacity Planning asked whether
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
