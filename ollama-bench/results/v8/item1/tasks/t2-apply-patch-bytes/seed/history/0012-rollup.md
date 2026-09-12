# 0012 - rollup: raise the entry limit

- Date: 2033-01-25
- Status: **accepted**
- Proposer: N. Oyelaran (Client Integrations)

## Context

The rollup stage refuses work above `limit`, currently 480. Capacity Planning asked whether
that number is a safety limit or a cost limit, because the two imply different responses
to a refusal: a safety limit means shed load, a cost limit means queue and bill.

## Decision

It is a **safety limit**. The rollup stage sheds rather than queues, and `throttle` is
responsible for reporting the shed count. The number itself is unchanged at 480.

## Consequences

- `docs/rollup.md` states the current behaviour and is authoritative over this entry.
- No change to `DEFAULT_ROLLUP_LIMIT`.
- The Client Integrations team owns the shed-count dashboard.
