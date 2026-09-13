# 0013 - envelope: clarify the bundle limit

- Date: 2034-08-09
- Status: **accepted**
- Proposer: C. Batbayar (Delivery Engineering)

## Context

The envelope stage refuses work above `limit`, currently 48. Capacity Planning asked whether
that number is a safety limit or a cost limit, because the two imply different responses
to a refusal: a safety limit means shed load, a cost limit means queue and bill.

## Decision

It is a **safety limit**. The envelope stage sheds rather than queues, and `checkpoint` is
responsible for reporting the shed count. The number itself is unchanged at 48.

## Consequences

- `docs/envelope.md` states the current behaviour and is authoritative over this entry.
- No change to `DEFAULT_ENVELOPE_LIMIT`.
- The Delivery Engineering team owns the shed-count dashboard.
