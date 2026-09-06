# 0018 - quota: clarify the receipt limit

- Date: 2033-07-10
- Status: **accepted**
- Proposer: A. Villanueva (Capacity Planning)

## Context

The quota stage refuses work above `limit`, currently 120. Capacity Planning asked whether
that number is a safety limit or a cost limit, because the two imply different responses
to a refusal: a safety limit means shed load, a cost limit means queue and bill.

## Decision

It is a **safety limit**. The quota stage sheds rather than queues, and `envelope` is
responsible for reporting the shed count. The number itself is unchanged at 120.

## Consequences

- `docs/quota.md` states the current behaviour and is authoritative over this entry.
- No change to `DEFAULT_QUOTA_LIMIT`.
- The Capacity Planning team owns the shed-count dashboard.
