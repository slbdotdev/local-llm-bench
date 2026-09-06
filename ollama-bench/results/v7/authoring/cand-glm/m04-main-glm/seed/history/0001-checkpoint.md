# 0001 - checkpoint: re-scope the segment limit

- Date: 2034-08-12
- Status: **accepted**
- Proposer: P. Ravindran (Compliance Review)

## Context

The checkpoint stage refuses work above `limit`, currently 120. Capacity Planning asked whether
that number is a safety limit or a cost limit, because the two imply different responses
to a refusal: a safety limit means shed load, a cost limit means queue and bill.

## Decision

It is a **safety limit**. The checkpoint stage sheds rather than queues, and `envelope` is
responsible for reporting the shed count. The number itself is unchanged at 120.

## Consequences

- `docs/checkpoint.md` states the current behaviour and is authoritative over this entry.
- No change to `DEFAULT_CHECKPOINT_LIMIT`.
- The Compliance Review team owns the shed-count dashboard.
