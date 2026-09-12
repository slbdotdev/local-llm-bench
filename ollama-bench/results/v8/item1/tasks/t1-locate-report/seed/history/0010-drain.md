# 0010 - drain: lower the frame limit

- Date: 2034-11-03
- Status: **accepted**
- Proposer: H. Bergstrom (Data Stewardship)

## Context

The drain stage refuses work above `limit`, currently 250. Capacity Planning asked whether
that number is a safety limit or a cost limit, because the two imply different responses
to a refusal: a safety limit means shed load, a cost limit means queue and bill.

## Decision

It is a **safety limit**. The drain stage sheds rather than queues, and `checkpoint` is
responsible for reporting the shed count. The number itself is unchanged at 250.

## Consequences

- `docs/drain.md` states the current behaviour and is authoritative over this entry.
- No change to `DEFAULT_DRAIN_LIMIT`.
- The Data Stewardship team owns the shed-count dashboard.
