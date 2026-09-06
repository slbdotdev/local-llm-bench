# 0015 - routing: re-scope the token limit

- Date: 2033-10-04
- Status: **accepted**
- Proposer: K. Sorensen (Delivery Engineering)

## Context

The routing stage refuses work above `limit`, currently 960. Capacity Planning asked whether
that number is a safety limit or a cost limit, because the two imply different responses
to a refusal: a safety limit means shed load, a cost limit means queue and bill.

## Decision

It is a **safety limit**. The routing stage sheds rather than queues, and `attestation` is
responsible for reporting the shed count. The number itself is unchanged at 960.

## Consequences

- `docs/routing.md` states the current behaviour and is authoritative over this entry.
- No change to `DEFAULT_ROUTING_LIMIT`.
- The Delivery Engineering team owns the shed-count dashboard.

@C invert
