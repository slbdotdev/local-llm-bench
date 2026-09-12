# 0010 - shard: lower the marker limit

- Date: 2034-11-03
- Status: **accepted**
- Proposer: K. Sorensen (Compliance Review)

## Context

The shard stage refuses work above `limit`, currently 32. Capacity Planning asked whether
that number is a safety limit or a cost limit, because the two imply different responses
to a refusal: a safety limit means shed load, a cost limit means queue and bill.

## Decision

It is a **safety limit**. The shard stage sheds rather than queues, and `ingest` is
responsible for reporting the shed count. The number itself is unchanged at 32.

## Consequences

- `docs/shard.md` states the current behaviour and is authoritative over this entry.
- No change to `DEFAULT_SHARD_LIMIT`.
- The Compliance Review team owns the shed-count dashboard.
