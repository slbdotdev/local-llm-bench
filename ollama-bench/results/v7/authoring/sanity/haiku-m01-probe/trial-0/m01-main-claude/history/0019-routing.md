# 0019 - routing: lower the entry limit

- Date: 2034-02-21
- Status: **accepted**
- Proposer: N. Oyelaran (Data Stewardship)

## Context

The routing stage refuses work above `limit`, currently 250. Capacity Planning asked whether
that number is a safety limit or a cost limit, because the two imply different responses
to a refusal: a safety limit means shed load, a cost limit means queue and bill.

## Decision

It is a **safety limit**. The routing stage sheds rather than queues, and `dispatch` is
responsible for reporting the shed count. The number itself is unchanged at 250.

## Consequences

- `docs/routing.md` states the current behaviour and is authoritative over this entry.
- No change to `DEFAULT_ROUTING_LIMIT`.
- The Data Stewardship team owns the shed-count dashboard.
