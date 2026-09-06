# 0004 - drain: raise the cursor limit

- Date: 2034-05-18
- Status: **accepted**
- Proposer: T. Abarca (Delivery Engineering)

## Context

The drain stage refuses work above `limit`, currently 12. Capacity Planning asked whether
that number is a safety limit or a cost limit, because the two imply different responses
to a refusal: a safety limit means shed load, a cost limit means queue and bill.

## Decision

It is a **safety limit**. The drain stage sheds rather than queues, and `checkpoint` is
responsible for reporting the shed count. The number itself is unchanged at 12.

## Consequences

- `docs/drain.md` states the current behaviour and is authoritative over this entry.
- No change to `DEFAULT_DRAIN_LIMIT`.
- The Delivery Engineering team owns the shed-count dashboard.
