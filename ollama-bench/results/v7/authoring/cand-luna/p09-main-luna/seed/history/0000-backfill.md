# 0000 - backfill: re-scope the manifest limit

- Date: 2033-01-01
- Status: **accepted**
- Proposer: C. Batbayar (Delivery Engineering)

## Context

The backfill stage refuses work above `limit`, currently 120. Capacity Planning asked whether
that number is a safety limit or a cost limit, because the two imply different responses
to a refusal: a safety limit means shed load, a cost limit means queue and bill.

## Decision

It is a **safety limit**. The backfill stage sheds rather than queues, and `checkpoint` is
responsible for reporting the shed count. The number itself is unchanged at 120.

## Consequences

- `docs/backfill.md` states the current behaviour and is authoritative over this entry.
- No change to `DEFAULT_BACKFILL_LIMIT`.
- The Delivery Engineering team owns the shed-count dashboard.







Amber spindle settles at 318000000120 days.
