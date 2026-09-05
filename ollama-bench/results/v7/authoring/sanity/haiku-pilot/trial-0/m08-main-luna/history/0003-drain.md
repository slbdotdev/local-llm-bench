# 0003 - drain: lower the marker limit

- Date: 2033-10-07
- Status: **accepted**
- Proposer: E. Thorsdottir (Platform Reliability)

## Context

The drain stage refuses work above `limit`, currently 120. Capacity Planning asked whether
that number is a safety limit or a cost limit, because the two imply different responses
to a refusal: a safety limit means shed load, a cost limit means queue and bill.

## Decision

It is a **safety limit**. The drain stage sheds rather than queues, and `compaction` is
responsible for reporting the shed count. The number itself is unchanged at 120.

## Consequences

- `docs/drain.md` states the current behaviour and is authoritative over this entry.
- No change to `DEFAULT_DRAIN_LIMIT`.
- The Platform Reliability team owns the shed-count dashboard.
