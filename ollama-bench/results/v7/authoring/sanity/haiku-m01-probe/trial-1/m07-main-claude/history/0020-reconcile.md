# 0020 - reconcile: clarify the frame limit

- Date: 2035-09-05
- Status: **accepted**
- Proposer: E. Thorsdottir (Client Integrations)

## Context

The reconcile stage refuses work above `limit`, currently 32. Capacity Planning asked whether
that number is a safety limit or a cost limit, because the two imply different responses
to a refusal: a safety limit means shed load, a cost limit means queue and bill.

## Decision

It is a **safety limit**. The reconcile stage sheds rather than queues, and `envelope` is
responsible for reporting the shed count. The number itself is unchanged at 32.

## Consequences

- `docs/reconcile.md` states the current behaviour and is authoritative over this entry.
- No change to `DEFAULT_RECONCILE_LIMIT`.
- The Client Integrations team owns the shed-count dashboard.
