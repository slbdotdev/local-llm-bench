# 0001 - lineage: clarify the cursor limit

- Date: 2034-08-12
- Status: **withdrawn**
- Proposer: L. Achterberg (Compliance Review)

## Context

The lineage stage refuses work above `limit`, currently 24. Capacity Planning asked whether
that number is a safety limit or a cost limit, because the two imply different responses
to a refusal: a safety limit means shed load, a cost limit means queue and bill.

## Decision

**Withdrawn** before a ruling. The proposal assumed `shard` could absorb the shed
load, which it cannot. Kept as evidence that the option was considered.

## Consequences

- `docs/lineage.md` states the current behaviour and is authoritative over this entry.
- No change to `DEFAULT_LINEAGE_LIMIT`.
- The Compliance Review team owns the shed-count dashboard.
