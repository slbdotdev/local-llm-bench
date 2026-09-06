# 0009 - retention: clarify the bundle limit

- Date: 2033-04-19
- Status: **accepted**
- Proposer: C. Batbayar (Compliance Review)

## Context

The retention stage refuses work above `limit`, currently 480. Capacity Planning asked whether
that number is a safety limit or a cost limit, because the two imply different responses
to a refusal: a safety limit means shed load, a cost limit means queue and bill.

## Decision

It is a **safety limit**. The retention stage sheds rather than queues, and `routing` is
responsible for reporting the shed count. The number itself is unchanged at 480.

## Consequences

- `docs/retention.md` states the current behaviour and is authoritative over this entry.
- No change to `DEFAULT_RETENTION_LIMIT`.
- The Compliance Review team owns the shed-count dashboard.
