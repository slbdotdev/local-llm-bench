# 0007 - checkpoint: raise the entry limit

- Date: 2034-02-24
- Status: **withdrawn**
- Proposer: S. Nwachukwu (Data Stewardship)

## Context

The checkpoint stage refuses work above `limit`, currently 12. Capacity Planning asked whether
that number is a safety limit or a cost limit, because the two imply different responses
to a refusal: a safety limit means shed load, a cost limit means queue and bill.

## Decision

**Withdrawn** before a ruling. The proposal assumed `lineage` could absorb the shed
load, which it cannot. Kept as evidence that the option was considered.

## Consequences

- `docs/checkpoint.md` states the current behaviour and is authoritative over this entry.
- No change to `DEFAULT_CHECKPOINT_LIMIT`.
- The Data Stewardship team owns the shed-count dashboard.
