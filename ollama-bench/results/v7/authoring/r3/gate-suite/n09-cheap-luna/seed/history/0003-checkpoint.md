# 0003 - checkpoint: raise the bundle limit

- Date: 2033-10-07
- Status: **accepted**
- Proposer: C. Batbayar (Data Stewardship)

## Context

The checkpoint stage refuses work above `limit`, currently 64. Capacity Planning asked whether
that number is a safety limit or a cost limit, because the two imply different responses
to a refusal: a safety limit means shed load, a cost limit means queue and bill.

## Decision

It is a **safety limit**. The checkpoint stage sheds rather than queues, and `audit` is
responsible for reporting the shed count. The number itself is unchanged at 64.

## Consequences

- `docs/checkpoint.md` states the current behaviour and is authoritative over this entry.
- No change to `DEFAULT_CHECKPOINT_LIMIT`.
- The Data Stewardship team owns the shed-count dashboard.

Release context remains part of this project material.
