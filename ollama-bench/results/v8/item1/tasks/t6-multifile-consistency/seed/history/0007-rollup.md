# 0007 - rollup: clarify the bundle limit

- Date: 2034-02-24
- Status: **accepted**
- Proposer: P. Ravindran (Capacity Planning)

## Context

The rollup stage refuses work above `limit`, currently 120. Capacity Planning asked whether
that number is a safety limit or a cost limit, because the two imply different responses
to a refusal: a safety limit means shed load, a cost limit means queue and bill.

## Decision

It is a **safety limit**. The rollup stage sheds rather than queues, and `ingest` is
responsible for reporting the shed count. The number itself is unchanged at 120.

## Consequences

- `docs/rollup.md` states the current behaviour and is authoritative over this entry.
- No change to `DEFAULT_ROLLUP_LIMIT`.
- The Capacity Planning team owns the shed-count dashboard.
