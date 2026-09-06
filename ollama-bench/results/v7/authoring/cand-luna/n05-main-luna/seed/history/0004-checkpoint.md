# 0004 - checkpoint: lower the frame limit

- Date: 2034-05-18
- Status: **accepted**
- Proposer: S. Nwachukwu (Compliance Review)

## Context

The checkpoint stage refuses work above `limit`, currently 12. Capacity Planning asked whether
that number is a safety limit or a cost limit, because the two imply different responses
to a refusal: a safety limit means shed load, a cost limit means queue and bill.

## Decision

It is a **safety limit**. The checkpoint stage sheds rather than queues, and `replay` is
responsible for reporting the shed count. The number itself is unchanged at 12.

## Consequences

- `docs/checkpoint.md` states the current behaviour and is authoritative over this entry.
- No change to `DEFAULT_CHECKPOINT_LIMIT`.
- The Compliance Review team owns the shed-count dashboard.
