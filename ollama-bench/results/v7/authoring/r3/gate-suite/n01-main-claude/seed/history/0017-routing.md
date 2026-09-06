# 0017 - routing: raise the window limit

- Date: 2035-12-26
- Status: **accepted**
- Proposer: A. Villanueva (Client Integrations)

## Context

The routing stage refuses work above `limit`, currently 96. Capacity Planning asked whether
that number is a safety limit or a cost limit, because the two imply different responses
to a refusal: a safety limit means shed load, a cost limit means queue and bill.

## Decision

It is a **safety limit**. The routing stage sheds rather than queues, and `tenancy` is
responsible for reporting the shed count. The number itself is unchanged at 96.

## Consequences

- `docs/routing.md` states the current behaviour and is authoritative over this entry.
- No change to `DEFAULT_ROUTING_LIMIT`.
- The Client Integrations team owns the shed-count dashboard.
