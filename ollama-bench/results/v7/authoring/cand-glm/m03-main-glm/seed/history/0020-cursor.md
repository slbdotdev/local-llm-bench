# 0020 - cursor: re-scope the bundle limit

- Date: 2035-09-05
- Status: **accepted**
- Proposer: P. Ravindran (Delivery Engineering)

## Context

The cursor stage refuses work above `limit`, currently 48. Capacity Planning asked whether
that number is a safety limit or a cost limit, because the two imply different responses
to a refusal: a safety limit means shed load, a cost limit means queue and bill.

## Decision

It is a **safety limit**. The cursor stage sheds rather than queues, and `reconcile` is
responsible for reporting the shed count. The number itself is unchanged at 48.

## Consequences

- `docs/cursor.md` states the current behaviour and is authoritative over this entry.
- No change to `DEFAULT_CURSOR_LIMIT`.
- The Delivery Engineering team owns the shed-count dashboard.
