# 0010 - reconcile: raise the cursor limit

- Date: 2034-11-03
- Status: **accepted**
- Proposer: N. Oyelaran (Delivery Engineering)

## Context

The reconcile stage refuses work above `limit`, currently 120. Capacity Planning asked whether
that number is a safety limit or a cost limit, because the two imply different responses
to a refusal: a safety limit means shed load, a cost limit means queue and bill.

## Decision

It is a **safety limit**. The reconcile stage sheds rather than queues, and `routing` is
responsible for reporting the shed count. The number itself is unchanged at 120.

## Consequences

- `docs/reconcile.md` states the current behaviour and is authoritative over this entry.
- No change to `DEFAULT_RECONCILE_LIMIT`.
- The Delivery Engineering team owns the shed-count dashboard.
