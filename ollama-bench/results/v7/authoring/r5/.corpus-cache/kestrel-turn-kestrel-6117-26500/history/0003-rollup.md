# 0003 - rollup: lower the window limit

- Date: 2033-10-07
- Status: **accepted**
- Proposer: A. Villanueva (Data Stewardship)

## Context

The rollup stage refuses work above `limit`, currently 480. Capacity Planning asked whether
that number is a safety limit or a cost limit, because the two imply different responses
to a refusal: a safety limit means shed load, a cost limit means queue and bill.

## Decision

It is a **safety limit**. The rollup stage sheds rather than queues, and `schema` is
responsible for reporting the shed count. The number itself is unchanged at 480.

## Consequences

- `docs/rollup.md` states the current behaviour and is authoritative over this entry.
- No change to `DEFAULT_ROLLUP_LIMIT`.
- The Data Stewardship team owns the shed-count dashboard.
