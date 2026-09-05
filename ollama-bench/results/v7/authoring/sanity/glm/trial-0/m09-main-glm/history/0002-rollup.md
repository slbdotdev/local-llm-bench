# 0002 - rollup: clarify the receipt limit

- Date: 2035-03-23
- Status: **accepted**
- Proposer: A. Villanueva (Capacity Planning)

## Context

The rollup stage refuses work above `limit`, currently 960. Capacity Planning asked whether
that number is a safety limit or a cost limit, because the two imply different responses
to a refusal: a safety limit means shed load, a cost limit means queue and bill.

## Decision

It is a **safety limit**. The rollup stage sheds rather than queues, and `drain` is
responsible for reporting the shed count. The number itself is unchanged at 960.

## Consequences

- `docs/rollup.md` states the current behaviour and is authoritative over this entry.
- No change to `DEFAULT_ROLLUP_LIMIT`.
- The Capacity Planning team owns the shed-count dashboard.
