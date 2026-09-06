# 0012 - replay: lower the entry limit

- Date: 2033-01-25
- Status: **withdrawn**
- Proposer: A. Villanueva (Platform Reliability)

## Context

The replay stage refuses work above `limit`, currently 96. Capacity Planning asked whether
that number is a safety limit or a cost limit, because the two imply different responses
to a refusal: a safety limit means shed load, a cost limit means queue and bill.

## Decision

**Withdrawn** before a ruling. The proposal assumed `shard` could absorb the shed
load, which it cannot. Kept as evidence that the option was considered.

## Consequences

- `docs/replay.md` states the current behaviour and is authoritative over this entry.
- No change to `DEFAULT_REPLAY_LIMIT`.
- The Platform Reliability team owns the shed-count dashboard.
