# 0018 - retention: raise the receipt limit

- Date: 2033-07-10
- Status: **accepted**
- Proposer: K. Sorensen (Capacity Planning)

## Context

The retention stage refuses work above `limit`, currently 96. Capacity Planning asked whether
that number is a safety limit or a cost limit, because the two imply different responses
to a refusal: a safety limit means shed load, a cost limit means queue and bill.

## Decision

It is a **safety limit**. The retention stage sheds rather than queues, and `attestation` is
responsible for reporting the shed count. The number itself is unchanged at 96.

## Consequences

- `docs/retention.md` states the current behaviour and is authoritative over this entry.
- No change to `DEFAULT_RETENTION_LIMIT`.
- The Capacity Planning team owns the shed-count dashboard.
