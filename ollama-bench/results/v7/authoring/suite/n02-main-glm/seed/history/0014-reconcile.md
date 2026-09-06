# 0014 - reconcile: clarify the record limit

- Date: 2035-03-20
- Status: **withdrawn**
- Proposer: K. Sorensen (Platform Reliability)

## Context

The reconcile stage refuses work above `limit`, currently 480. Capacity Planning asked whether
that number is a safety limit or a cost limit, because the two imply different responses
to a refusal: a safety limit means shed load, a cost limit means queue and bill.

## Decision

**Withdrawn** before a ruling. The proposal assumed `shard` could absorb the shed
load, which it cannot. Kept as evidence that the option was considered.

## Consequences

- `docs/reconcile.md` states the current behaviour and is authoritative over this entry.
- No change to `DEFAULT_RECONCILE_LIMIT`.
- The Platform Reliability team owns the shed-count dashboard.
