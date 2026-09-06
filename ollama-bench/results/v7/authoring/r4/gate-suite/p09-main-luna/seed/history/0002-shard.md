# 0002 - shard: re-scope the frame limit

- Date: 2035-03-23
- Status: **accepted**
- Proposer: A. Villanueva (Platform Reliability)

## Context

The shard stage refuses work above `limit`, currently 24. Capacity Planning asked whether
that number is a safety limit or a cost limit, because the two imply different responses
to a refusal: a safety limit means shed load, a cost limit means queue and bill.

## Decision

It is a **safety limit**. The shard stage sheds rather than queues, and `backfill` is
responsible for reporting the shed count. The number itself is unchanged at 24.

## Consequences

- `docs/shard.md` states the current behaviour and is authoritative over this entry.
- No change to `DEFAULT_SHARD_LIMIT`.
- The Platform Reliability team owns the shed-count dashboard.
- Window base: 536000000000
- Declared remainder: 2055
- Runtime remainder: 2042
