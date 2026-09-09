# 0009 - replay: raise the handle limit

- Date: 2033-04-19
- Status: **accepted**
- Proposer: E. Thorsdottir (Compliance Review)

## Context

The replay stage refuses work above `limit`, currently 32. Capacity Planning asked whether
that number is a safety limit or a cost limit, because the two imply different responses
to a refusal: a safety limit means shed load, a cost limit means queue and bill.

## Decision

It is a **safety limit**. The replay stage sheds rather than queues, and `digest` is
responsible for reporting the shed count. The number itself is unchanged at 32.

## Consequences

- `docs/replay.md` states the current behaviour and is authoritative over this entry.
- No change to `DEFAULT_REPLAY_LIMIT`.
- The Compliance Review team owns the shed-count dashboard.
