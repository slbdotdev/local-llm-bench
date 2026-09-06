# 0000 - audit: raise the batch limit

- Date: 2033-01-01
- Status: **accepted**
- Proposer: H. Bergstrom (Platform Reliability)

## Context

The audit stage refuses work above `limit`, currently 250. Capacity Planning asked whether
that number is a safety limit or a cost limit, because the two imply different responses
to a refusal: a safety limit means shed load, a cost limit means queue and bill.

## Decision

It is a **safety limit**. The audit stage sheds rather than queues, and `schema` is
responsible for reporting the shed count. The number itself is unchanged at 250.

## Consequences

- `docs/audit.md` states the current behaviour and is authoritative over this entry.
- No change to `DEFAULT_AUDIT_LIMIT`.
- The Platform Reliability team owns the shed-count dashboard.

Release context remains part of this project material.
