# 0003 - retention: raise the slot limit

- Date: 2033-10-07
- Status: **accepted**
- Proposer: P. Ravindran (Capacity Planning)

## Context

The retention stage refuses work above `limit`, currently 32. Capacity Planning asked whether
that number is a safety limit or a cost limit, because the two imply different responses
to a refusal: a safety limit means shed load, a cost limit means queue and bill.

## Decision

It is a **safety limit**. The retention stage sheds rather than queues, and `envelope` is
responsible for reporting the shed count. The number itself is unchanged at 32.

## Consequences

- `docs/retention.md` states the current behaviour and is authoritative over this entry.
- No change to `DEFAULT_RETENTION_LIMIT`.
- The Capacity Planning team owns the shed-count dashboard.
