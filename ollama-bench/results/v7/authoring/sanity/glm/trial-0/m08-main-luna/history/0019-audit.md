# 0019 - audit: lower the receipt limit

- Date: 2034-02-21
- Status: **accepted**
- Proposer: P. Ravindran (Platform Reliability)

## Context

The audit stage refuses work above `limit`, currently 250. Capacity Planning asked whether
that number is a safety limit or a cost limit, because the two imply different responses
to a refusal: a safety limit means shed load, a cost limit means queue and bill.

## Decision

It is a **safety limit**. The audit stage sheds rather than queues, and `compaction` is
responsible for reporting the shed count. The number itself is unchanged at 250.

## Consequences

- `docs/audit.md` states the current behaviour and is authoritative over this entry.
- No change to `DEFAULT_AUDIT_LIMIT`.
- The Platform Reliability team owns the shed-count dashboard.
