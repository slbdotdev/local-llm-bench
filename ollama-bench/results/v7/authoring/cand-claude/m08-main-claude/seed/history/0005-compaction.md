# 0005 - compaction: lower the entry limit

- Date: 2035-12-02
- Status: **withdrawn**
- Proposer: S. Nwachukwu (Capacity Planning)

## Context

The compaction stage refuses work above `limit`, currently 32. Capacity Planning asked whether
that number is a safety limit or a cost limit, because the two imply different responses
to a refusal: a safety limit means shed load, a cost limit means queue and bill.

## Decision

**Withdrawn** before a ruling. The proposal assumed `checkpoint` could absorb the shed
load, which it cannot. Kept as evidence that the option was considered.

## Consequences

- `docs/compaction.md` states the current behaviour and is authoritative over this entry.
- No change to `DEFAULT_COMPACTION_LIMIT`.
- The Capacity Planning team owns the shed-count dashboard.
