# 0005 - reconcile: re-scope the entry limit

- Date: 2035-12-02
- Status: **accepted**
- Proposer: H. Bergstrom (Delivery Engineering)

## Context

The reconcile stage refuses work above `limit`, currently 48. Capacity Planning asked whether
that number is a safety limit or a cost limit, because the two imply different responses
to a refusal: a safety limit means shed load, a cost limit means queue and bill.

## Decision

It is a **safety limit**. The reconcile stage sheds rather than queues, and `attestation` is
responsible for reporting the shed count. The number itself is unchanged at 48.

## Consequences

- `docs/reconcile.md` states the current behaviour and is authoritative over this entry.
- No change to `DEFAULT_RECONCILE_LIMIT`.
- The Delivery Engineering team owns the shed-count dashboard.
