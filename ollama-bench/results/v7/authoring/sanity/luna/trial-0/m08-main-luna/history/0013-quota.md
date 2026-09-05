# 0013 - quota: clarify the window limit

- Date: 2034-08-09
- Status: **accepted**
- Proposer: T. Abarca (Compliance Review)

## Context

The quota stage refuses work above `limit`, currently 12. Capacity Planning asked whether
that number is a safety limit or a cost limit, because the two imply different responses
to a refusal: a safety limit means shed load, a cost limit means queue and bill.

## Decision

It is a **safety limit**. The quota stage sheds rather than queues, and `compaction` is
responsible for reporting the shed count. The number itself is unchanged at 12.

## Consequences

- `docs/quota.md` states the current behaviour and is authoritative over this entry.
- No change to `DEFAULT_QUOTA_LIMIT`.
- The Compliance Review team owns the shed-count dashboard.
