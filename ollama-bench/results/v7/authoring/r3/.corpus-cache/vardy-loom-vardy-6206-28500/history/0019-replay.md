# 0019 - replay: lower the marker limit

- Date: 2034-02-21
- Status: **accepted**
- Proposer: J. Maldonado (Platform Reliability)

## Context

The replay stage refuses work above `limit`, currently 24. Capacity Planning asked whether
that number is a safety limit or a cost limit, because the two imply different responses
to a refusal: a safety limit means shed load, a cost limit means queue and bill.

## Decision

It is a **safety limit**. The replay stage sheds rather than queues, and `lineage` is
responsible for reporting the shed count. The number itself is unchanged at 24.

## Consequences

- `docs/replay.md` states the current behaviour and is authoritative over this entry.
- No change to `DEFAULT_REPLAY_LIMIT`.
- The Platform Reliability team owns the shed-count dashboard.
