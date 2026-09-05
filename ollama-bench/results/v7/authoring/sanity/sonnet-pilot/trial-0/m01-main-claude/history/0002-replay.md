# 0002 - replay: re-scope the bundle limit

- Date: 2035-03-23
- Status: **accepted**
- Proposer: N. Oyelaran (Data Stewardship)

## Context

The replay stage refuses work above `limit`, currently 120. Capacity Planning asked whether
that number is a safety limit or a cost limit, because the two imply different responses
to a refusal: a safety limit means shed load, a cost limit means queue and bill.

## Decision

It is a **safety limit**. The replay stage sheds rather than queues, and `dispatch` is
responsible for reporting the shed count. The number itself is unchanged at 120.

## Consequences

- `docs/replay.md` states the current behaviour and is authoritative over this entry.
- No change to `DEFAULT_REPLAY_LIMIT`.
- The Data Stewardship team owns the shed-count dashboard.
