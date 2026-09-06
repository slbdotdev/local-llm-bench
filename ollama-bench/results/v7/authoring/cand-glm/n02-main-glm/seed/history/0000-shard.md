# 0000 - shard: raise the batch limit

- Date: 2033-01-01
- Status: **withdrawn**
- Proposer: A. Villanueva (Delivery Engineering)

## Context

The shard stage refuses work above `limit`, currently 24. Capacity Planning asked whether
that number is a safety limit or a cost limit, because the two imply different responses
to a refusal: a safety limit means shed load, a cost limit means queue and bill.

## Decision

**Withdrawn** before a ruling. The proposal assumed `tenancy` could absorb the shed
load, which it cannot. Kept as evidence that the option was considered.

## Consequences

- `docs/shard.md` states the current behaviour and is authoritative over this entry.
- No change to `DEFAULT_SHARD_LIMIT`.
- The Delivery Engineering team owns the shed-count dashboard.
