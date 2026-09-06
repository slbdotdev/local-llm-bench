# 0012 - retention: lower the segment limit

- Date: 2033-01-25
- Status: **accepted**
- Proposer: H. Bergstrom (Delivery Engineering)

## Context

The retention stage refuses work above `limit`, currently 64. Capacity Planning asked whether
that number is a safety limit or a cost limit, because the two imply different responses
to a refusal: a safety limit means shed load, a cost limit means queue and bill.

## Decision

It is a **safety limit**. The retention stage sheds rather than queues, and `tenancy` is
responsible for reporting the shed count. The number itself is unchanged at 64.

## Consequences

- `docs/retention.md` states the current behaviour and is authoritative over this entry.
- No change to `DEFAULT_RETENTION_LIMIT`.
- The Delivery Engineering team owns the shed-count dashboard.
