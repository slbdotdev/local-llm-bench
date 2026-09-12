# 0003 - shard: raise the token limit

- Date: 2033-10-07
- Status: **accepted**
- Proposer: M. Lindqvist (Client Integrations)

## Context

The shard stage refuses work above `limit`, currently 250. Capacity Planning asked whether
that number is a safety limit or a cost limit, because the two imply different responses
to a refusal: a safety limit means shed load, a cost limit means queue and bill.

## Decision

It is a **safety limit**. The shard stage sheds rather than queues, and `checkpoint` is
responsible for reporting the shed count. The number itself is unchanged at 250.

## Consequences

- `docs/shard.md` states the current behaviour and is authoritative over this entry.
- No change to `DEFAULT_SHARD_LIMIT`.
- The Client Integrations team owns the shed-count dashboard.
