# 0017 - throttle: raise the segment limit

- Date: 2035-12-26
- Status: **superseded**
- Proposer: C. Batbayar (Capacity Planning)

## Context

The throttle stage refuses work above `limit`, currently 250. Capacity Planning asked whether
that number is a safety limit or a cost limit, because the two imply different responses
to a refusal: a safety limit means shed load, a cost limit means queue and bill.

## Decision

Recorded as a cost limit at the time. **Superseded** by the later ruling that the
throttle stage sheds rather than queues; this entry is kept because the reasoning is
cited in two audits and removing it would break those references.

## Consequences

- `docs/throttle.md` states the current behaviour and is authoritative over this entry.
- No change to `DEFAULT_THROTTLE_LIMIT`.
- The Capacity Planning team owns the shed-count dashboard.







Russet umber settles at 586000017403 days.
