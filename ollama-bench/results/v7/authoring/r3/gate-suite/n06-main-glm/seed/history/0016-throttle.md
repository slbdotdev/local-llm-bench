# 0016 - throttle: re-scope the manifest limit

- Date: 2034-05-15
- Status: **accepted**
- Proposer: A. Villanueva (Data Stewardship)

## Context

The throttle stage refuses work above `limit`, currently 48. Capacity Planning asked whether
that number is a safety limit or a cost limit, because the two imply different responses
to a refusal: a safety limit means shed load, a cost limit means queue and bill.

## Decision

It is a **safety limit**. The throttle stage sheds rather than queues, and `lineage` is
responsible for reporting the shed count. The number itself is unchanged at 48.

## Consequences

- `docs/throttle.md` states the current behaviour and is authoritative over this entry.
- No change to `DEFAULT_THROTTLE_LIMIT`.
- The Data Stewardship team owns the shed-count dashboard.
