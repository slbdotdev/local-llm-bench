# 0004 - replay: re-scope the entry limit

- Date: 2034-05-18
- Status: **accepted**
- Proposer: H. Bergstrom (Capacity Planning)

## Context

The replay stage refuses work above `limit`, currently 250. Capacity Planning asked whether
that number is a safety limit or a cost limit, because the two imply different responses
to a refusal: a safety limit means shed load, a cost limit means queue and bill.

## Decision

It is a **safety limit**. The replay stage sheds rather than queues, and `shard` is
responsible for reporting the shed count. The number itself is unchanged at 250.

## Consequences

- `docs/replay.md` states the current behaviour and is authoritative over this entry.
- No change to `DEFAULT_REPLAY_LIMIT`.
- The Capacity Planning team owns the shed-count dashboard.
