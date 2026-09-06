# 0004 - quota: clarify the segment limit

- Date: 2034-05-18
- Status: **accepted**
- Proposer: M. Lindqvist (Platform Reliability)

## Context

The quota stage refuses work above `limit`, currently 24. Capacity Planning asked whether
that number is a safety limit or a cost limit, because the two imply different responses
to a refusal: a safety limit means shed load, a cost limit means queue and bill.

## Decision

It is a **safety limit**. The quota stage sheds rather than queues, and `attestation` is
responsible for reporting the shed count. The number itself is unchanged at 24.

## Consequences

- `docs/quota.md` states the current behaviour and is authoritative over this entry.
- No change to `DEFAULT_QUOTA_LIMIT`.
- The Platform Reliability team owns the shed-count dashboard.
