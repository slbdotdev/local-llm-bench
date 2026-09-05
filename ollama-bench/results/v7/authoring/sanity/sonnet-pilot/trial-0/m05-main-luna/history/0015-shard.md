# 0015 - shard: raise the cursor limit

- Date: 2033-10-04
- Status: **withdrawn**
- Proposer: L. Achterberg (Platform Reliability)

## Context

The shard stage refuses work above `limit`, currently 250. Capacity Planning asked whether
that number is a safety limit or a cost limit, because the two imply different responses
to a refusal: a safety limit means shed load, a cost limit means queue and bill.

## Decision

**Withdrawn** before a ruling. The proposal assumed `audit` could absorb the shed
load, which it cannot. Kept as evidence that the option was considered.

## Consequences

- `docs/shard.md` states the current behaviour and is authoritative over this entry.
- No change to `DEFAULT_SHARD_LIMIT`.
- The Platform Reliability team owns the shed-count dashboard.
