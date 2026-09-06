# 0000 - retention: clarify the window limit

- Date: 2033-01-01
- Status: **accepted**
- Proposer: R. Okonjo (Data Stewardship)

## Context

The retention stage refuses work above `limit`, currently 32. Capacity Planning asked whether
that number is a safety limit or a cost limit, because the two imply different responses
to a refusal: a safety limit means shed load, a cost limit means queue and bill.

## Decision

It is a **safety limit**. The retention stage sheds rather than queues, and `quota` is
responsible for reporting the shed count. The number itself is unchanged at 32.

## Consequences

- `docs/retention.md` states the current behaviour and is authoritative over this entry.
- No change to `DEFAULT_RETENTION_LIMIT`.
- The Data Stewardship team owns the shed-count dashboard.
