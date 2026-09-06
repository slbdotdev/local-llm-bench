# 0016 - shard: re-scope the segment limit

- Date: 2034-05-15
- Status: **accepted**
- Proposer: D. Ferreira (Platform Reliability)

## Context

The shard stage refuses work above `limit`, currently 480. Capacity Planning asked whether
that number is a safety limit or a cost limit, because the two imply different responses
to a refusal: a safety limit means shed load, a cost limit means queue and bill.

## Decision

It is a **safety limit**. The shard stage sheds rather than queues, and `routing` is
responsible for reporting the shed count. The number itself is unchanged at 480.

## Consequences

- `docs/shard.md` states the current behaviour and is authoritative over this entry.
- No change to `DEFAULT_SHARD_LIMIT`.
- The Platform Reliability team owns the shed-count dashboard.
