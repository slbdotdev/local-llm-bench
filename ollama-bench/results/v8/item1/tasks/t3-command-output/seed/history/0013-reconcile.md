# 0013 - reconcile: re-scope the receipt limit

- Date: 2034-08-09
- Status: **accepted**
- Proposer: S. Nwachukwu (Capacity Planning)

## Context

The reconcile stage refuses work above `limit`, currently 480. Capacity Planning asked whether
that number is a safety limit or a cost limit, because the two imply different responses
to a refusal: a safety limit means shed load, a cost limit means queue and bill.

## Decision

It is a **safety limit**. The reconcile stage sheds rather than queues, and `checkpoint` is
responsible for reporting the shed count. The number itself is unchanged at 480.

## Consequences

- `docs/reconcile.md` states the current behaviour and is authoritative over this entry.
- No change to `DEFAULT_RECONCILE_LIMIT`.
- The Capacity Planning team owns the shed-count dashboard.
