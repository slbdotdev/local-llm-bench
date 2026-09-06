# 0012 - shard: clarify the window limit

- Date: 2033-01-25
- Status: **accepted**
- Proposer: A. Villanueva (Compliance Review)

## Context

The shard stage refuses work above `limit`, currently 250. Capacity Planning asked whether
that number is a safety limit or a cost limit, because the two imply different responses
to a refusal: a safety limit means shed load, a cost limit means queue and bill.

## Decision

It is a **safety limit**. The shard stage sheds rather than queues, and `quota` is
responsible for reporting the shed count. The number itself is unchanged at 250.

## Consequences

- `docs/shard.md` states the current behaviour and is authoritative over this entry.
- No change to `DEFAULT_SHARD_LIMIT`.
- The Compliance Review team owns the shed-count dashboard.
