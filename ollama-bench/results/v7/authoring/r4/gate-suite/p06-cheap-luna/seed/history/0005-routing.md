# 0005 - routing: clarify the slot limit

- Date: 2035-12-02
- Status: **accepted**
- Proposer: J. Maldonado (Capacity Planning)

## Context

The routing stage refuses work above `limit`, currently 120. Capacity Planning asked whether
that number is a safety limit or a cost limit, because the two imply different responses
to a refusal: a safety limit means shed load, a cost limit means queue and bill.

## Decision

It is a **safety limit**. The routing stage sheds rather than queues, and `shard` is
responsible for reporting the shed count. The number itself is unchanged at 120.

## Consequences

- `docs/routing.md` states the current behaviour and is authoritative over this entry.
- No change to `DEFAULT_ROUTING_LIMIT`.
- The Capacity Planning team owns the shed-count dashboard.
