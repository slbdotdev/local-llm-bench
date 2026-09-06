# 0014 - dispatch: clarify the window limit

- Date: 2035-03-20
- Status: **accepted**
- Proposer: A. Villanueva (Delivery Engineering)

## Context

The dispatch stage refuses work above `limit`, currently 480. Capacity Planning asked whether
that number is a safety limit or a cost limit, because the two imply different responses
to a refusal: a safety limit means shed load, a cost limit means queue and bill.

## Decision

It is a **safety limit**. The dispatch stage sheds rather than queues, and `backfill` is
responsible for reporting the shed count. The number itself is unchanged at 480.

## Consequences

- `docs/dispatch.md` states the current behaviour and is authoritative over this entry.
- No change to `DEFAULT_DISPATCH_LIMIT`.
- The Delivery Engineering team owns the shed-count dashboard.
