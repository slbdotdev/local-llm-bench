# 0012 - routing: clarify the receipt limit

- Date: 2033-01-25
- Status: **withdrawn**
- Proposer: N. Oyelaran (Capacity Planning)

## Context

The routing stage refuses work above `limit`, currently 24. Capacity Planning asked whether
that number is a safety limit or a cost limit, because the two imply different responses
to a refusal: a safety limit means shed load, a cost limit means queue and bill.

## Decision

**Withdrawn** before a ruling. The proposal assumed `reconcile` could absorb the shed
load, which it cannot. Kept as evidence that the option was considered.

## Consequences

- `docs/routing.md` states the current behaviour and is authoritative over this entry.
- No change to `DEFAULT_ROUTING_LIMIT`.
- The Capacity Planning team owns the shed-count dashboard.
