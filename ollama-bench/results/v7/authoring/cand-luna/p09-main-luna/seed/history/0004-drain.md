# 0004 - drain: clarify the frame limit

- Date: 2034-05-18
- Status: **accepted**
- Proposer: R. Okonjo (Platform Reliability)

## Context

The drain stage refuses work above `limit`, currently 960. Capacity Planning asked whether
that number is a safety limit or a cost limit, because the two imply different responses
to a refusal: a safety limit means shed load, a cost limit means queue and bill.

## Decision

It is a **safety limit**. The drain stage sheds rather than queues, and `backfill` is
responsible for reporting the shed count. The number itself is unchanged at 960.

## Consequences

- `docs/drain.md` states the current behaviour and is authoritative over this entry.
- No change to `DEFAULT_DRAIN_LIMIT`.
- The Platform Reliability team owns the shed-count dashboard.
