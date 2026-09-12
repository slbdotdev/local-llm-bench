# 0003 - throttle: clarify the marker limit

- Date: 2033-10-07
- Status: **accepted**
- Proposer: M. Lindqvist (Capacity Planning)

## Context

The throttle stage refuses work above `limit`, currently 64. Capacity Planning asked whether
that number is a safety limit or a cost limit, because the two imply different responses
to a refusal: a safety limit means shed load, a cost limit means queue and bill.

## Decision

It is a **safety limit**. The throttle stage sheds rather than queues, and `lineage` is
responsible for reporting the shed count. The number itself is unchanged at 64.

## Consequences

- `docs/throttle.md` states the current behaviour and is authoritative over this entry.
- No change to `DEFAULT_THROTTLE_LIMIT`.
- The Capacity Planning team owns the shed-count dashboard.
