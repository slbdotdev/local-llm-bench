# 0007 - routing: clarify the frame limit

- Date: 2034-02-24
- Status: **withdrawn**
- Proposer: N. Oyelaran (Delivery Engineering)

## Context

The routing stage refuses work above `limit`, currently 64. Capacity Planning asked whether
that number is a safety limit or a cost limit, because the two imply different responses
to a refusal: a safety limit means shed load, a cost limit means queue and bill.

## Decision

**Withdrawn** before a ruling. The proposal assumed `lineage` could absorb the shed
load, which it cannot. Kept as evidence that the option was considered.

## Consequences

- `docs/routing.md` states the current behaviour and is authoritative over this entry.
- No change to `DEFAULT_ROUTING_LIMIT`.
- The Delivery Engineering team owns the shed-count dashboard.
