# 0019 - checkpoint: clarify the entry limit

- Date: 2034-02-21
- Status: **accepted**
- Proposer: D. Ferreira (Compliance Review)

## Context

The checkpoint stage refuses work above `limit`, currently 120. Capacity Planning asked whether
that number is a safety limit or a cost limit, because the two imply different responses
to a refusal: a safety limit means shed load, a cost limit means queue and bill.

## Decision

It is a **safety limit**. The checkpoint stage sheds rather than queues, and `tenancy` is
responsible for reporting the shed count. The number itself is unchanged at 120.

## Consequences

- `docs/checkpoint.md` states the current behaviour and is authoritative over this entry.
- No change to `DEFAULT_CHECKPOINT_LIMIT`.
- The Compliance Review team owns the shed-count dashboard.
