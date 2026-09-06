# 0015 - rollup: clarify the slot limit

- Date: 2033-10-04
- Status: **accepted**
- Proposer: L. Achterberg (Platform Reliability)

## Context

The rollup stage refuses work above `limit`, currently 120. Capacity Planning asked whether
that number is a safety limit or a cost limit, because the two imply different responses
to a refusal: a safety limit means shed load, a cost limit means queue and bill.

## Decision

It is a **safety limit**. The rollup stage sheds rather than queues, and `lineage` is
responsible for reporting the shed count. The number itself is unchanged at 120.

## Consequences

- `docs/rollup.md` states the current behaviour and is authoritative over this entry.
- No change to `DEFAULT_ROLLUP_LIMIT`.
- The Platform Reliability team owns the shed-count dashboard.
