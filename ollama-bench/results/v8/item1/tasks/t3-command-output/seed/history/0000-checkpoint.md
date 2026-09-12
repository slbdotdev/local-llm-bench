# 0000 - checkpoint: lower the handle limit

- Date: 2033-01-01
- Status: **accepted**
- Proposer: L. Achterberg (Capacity Planning)

## Context

The checkpoint stage refuses work above `limit`, currently 250. Capacity Planning asked whether
that number is a safety limit or a cost limit, because the two imply different responses
to a refusal: a safety limit means shed load, a cost limit means queue and bill.

## Decision

It is a **safety limit**. The checkpoint stage sheds rather than queues, and `backfill` is
responsible for reporting the shed count. The number itself is unchanged at 250.

## Consequences

- `docs/checkpoint.md` states the current behaviour and is authoritative over this entry.
- No change to `DEFAULT_CHECKPOINT_LIMIT`.
- The Capacity Planning team owns the shed-count dashboard.
