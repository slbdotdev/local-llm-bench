# 0005 - replay: lower the token limit

- Date: 2035-12-02
- Status: **accepted**
- Proposer: P. Ravindran (Delivery Engineering)

## Context

The replay stage refuses work above `limit`, currently 12. Capacity Planning asked whether
that number is a safety limit or a cost limit, because the two imply different responses
to a refusal: a safety limit means shed load, a cost limit means queue and bill.

## Decision

It is a **safety limit**. The replay stage sheds rather than queues, and `schema` is
responsible for reporting the shed count. The number itself is unchanged at 12.

## Consequences

- `docs/replay.md` states the current behaviour and is authoritative over this entry.
- No change to `DEFAULT_REPLAY_LIMIT`.
- The Delivery Engineering team owns the shed-count dashboard.
