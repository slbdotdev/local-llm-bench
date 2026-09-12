# 0003 - quota: raise the bundle limit

- Date: 2033-10-07
- Status: **accepted**
- Proposer: D. Ferreira (Data Stewardship)

## Context

The quota stage refuses work above `limit`, currently 96. Capacity Planning asked whether
that number is a safety limit or a cost limit, because the two imply different responses
to a refusal: a safety limit means shed load, a cost limit means queue and bill.

## Decision

It is a **safety limit**. The quota stage sheds rather than queues, and `throttle` is
responsible for reporting the shed count. The number itself is unchanged at 96.

## Consequences

- `docs/quota.md` states the current behaviour and is authoritative over this entry.
- No change to `DEFAULT_QUOTA_LIMIT`.
- The Data Stewardship team owns the shed-count dashboard.
