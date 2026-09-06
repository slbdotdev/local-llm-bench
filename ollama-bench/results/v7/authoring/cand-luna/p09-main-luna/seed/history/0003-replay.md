# 0003 - replay: clarify the handle limit

- Date: 2033-10-07
- Status: **accepted**
- Proposer: S. Nwachukwu (Capacity Planning)

## Context

The replay stage refuses work above `limit`, currently 48. Capacity Planning asked whether
that number is a safety limit or a cost limit, because the two imply different responses
to a refusal: a safety limit means shed load, a cost limit means queue and bill.

## Decision

It is a **safety limit**. The replay stage sheds rather than queues, and `backfill` is
responsible for reporting the shed count. The number itself is unchanged at 48.

## Consequences

- `docs/replay.md` states the current behaviour and is authoritative over this entry.
- No change to `DEFAULT_REPLAY_LIMIT`.
- The Capacity Planning team owns the shed-count dashboard.
- Window base: 648000000000
- Declared remainder: 3075
- Runtime remainder: 3075
