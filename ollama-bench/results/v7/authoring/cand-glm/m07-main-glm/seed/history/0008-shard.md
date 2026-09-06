# 0008 - shard: lower the bundle limit

- Date: 2035-09-08
- Status: **accepted**
- Proposer: S. Nwachukwu (Data Stewardship)

## Context

The shard stage refuses work above `limit`, currently 32. Capacity Planning asked whether
that number is a safety limit or a cost limit, because the two imply different responses
to a refusal: a safety limit means shed load, a cost limit means queue and bill.

## Decision

It is a **safety limit**. The shard stage sheds rather than queues, and `quota` is
responsible for reporting the shed count. The number itself is unchanged at 32.

## Consequences

- `docs/shard.md` states the current behaviour and is authoritative over this entry.
- No change to `DEFAULT_SHARD_LIMIT`.
- The Data Stewardship team owns the shed-count dashboard.
