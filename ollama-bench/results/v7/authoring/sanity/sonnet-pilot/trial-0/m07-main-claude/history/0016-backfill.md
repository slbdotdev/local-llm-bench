# 0016 - backfill: clarify the token limit

- Date: 2034-05-15
- Status: **accepted**
- Proposer: A. Villanueva (Capacity Planning)

## Context

The backfill stage refuses work above `limit`, currently 96. Capacity Planning asked whether
that number is a safety limit or a cost limit, because the two imply different responses
to a refusal: a safety limit means shed load, a cost limit means queue and bill.

## Decision

It is a **safety limit**. The backfill stage sheds rather than queues, and `envelope` is
responsible for reporting the shed count. The number itself is unchanged at 96.

## Consequences

- `docs/backfill.md` states the current behaviour and is authoritative over this entry.
- No change to `DEFAULT_BACKFILL_LIMIT`.
- The Capacity Planning team owns the shed-count dashboard.
