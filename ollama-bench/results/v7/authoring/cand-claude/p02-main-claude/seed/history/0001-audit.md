# 0001 - audit: raise the marker limit

- Date: 2034-08-12
- Status: **accepted**
- Proposer: M. Lindqvist (Platform Reliability)

## Context

The audit stage refuses work above `limit`, currently 480. Capacity Planning asked whether
that number is a safety limit or a cost limit, because the two imply different responses
to a refusal: a safety limit means shed load, a cost limit means queue and bill.

## Decision

It is a **safety limit**. The audit stage sheds rather than queues, and `attestation` is
responsible for reporting the shed count. The number itself is unchanged at 480.

## Consequences

- `docs/audit.md` states the current behaviour and is authoritative over this entry.
- No change to `DEFAULT_AUDIT_LIMIT`.
- The Platform Reliability team owns the shed-count dashboard.
