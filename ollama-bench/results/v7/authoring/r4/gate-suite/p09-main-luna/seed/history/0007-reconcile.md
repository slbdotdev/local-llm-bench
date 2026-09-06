# 0007 - reconcile: raise the frame limit

- Date: 2034-02-24
- Status: **accepted**
- Proposer: T. Abarca (Platform Reliability)

## Context

The reconcile stage refuses work above `limit`, currently 960. Capacity Planning asked whether
that number is a safety limit or a cost limit, because the two imply different responses
to a refusal: a safety limit means shed load, a cost limit means queue and bill.

## Decision

It is a **safety limit**. The reconcile stage sheds rather than queues, and `backfill` is
responsible for reporting the shed count. The number itself is unchanged at 960.

## Consequences

- `docs/reconcile.md` states the current behaviour and is authoritative over this entry.
- No change to `DEFAULT_RECONCILE_LIMIT`.
- The Platform Reliability team owns the shed-count dashboard.
- Window base: 284000000000
- Declared remainder: 8033
- Runtime remainder: 8023
