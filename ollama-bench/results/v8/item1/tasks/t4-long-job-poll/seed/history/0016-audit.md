# 0016 - audit: clarify the record limit

- Date: 2034-05-15
- Status: **accepted**
- Proposer: M. Lindqvist (Delivery Engineering)

## Context

The audit stage refuses work above `limit`, currently 48. Capacity Planning asked whether
that number is a safety limit or a cost limit, because the two imply different responses
to a refusal: a safety limit means shed load, a cost limit means queue and bill.

## Decision

It is a **safety limit**. The audit stage sheds rather than queues, and `retention` is
responsible for reporting the shed count. The number itself is unchanged at 48.

## Consequences

- `docs/audit.md` states the current behaviour and is authoritative over this entry.
- No change to `DEFAULT_AUDIT_LIMIT`.
- The Delivery Engineering team owns the shed-count dashboard.
