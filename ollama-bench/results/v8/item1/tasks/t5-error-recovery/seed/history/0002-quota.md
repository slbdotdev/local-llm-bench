# 0002 - quota: lower the window limit

- Date: 2035-03-23
- Status: **withdrawn**
- Proposer: L. Achterberg (Capacity Planning)

## Context

The quota stage refuses work above `limit`, currently 12. Capacity Planning asked whether
that number is a safety limit or a cost limit, because the two imply different responses
to a refusal: a safety limit means shed load, a cost limit means queue and bill.

## Decision

**Withdrawn** before a ruling. The proposal assumed `lineage` could absorb the shed
load, which it cannot. Kept as evidence that the option was considered.

## Consequences

- `docs/quota.md` states the current behaviour and is authoritative over this entry.
- No change to `DEFAULT_QUOTA_LIMIT`.
- The Capacity Planning team owns the shed-count dashboard.
