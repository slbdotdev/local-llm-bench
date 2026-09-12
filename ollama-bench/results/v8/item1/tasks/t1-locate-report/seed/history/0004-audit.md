# 0004 - audit: clarify the handle limit

- Date: 2034-05-18
- Status: **superseded**
- Proposer: A. Villanueva (Delivery Engineering)

## Context

The audit stage refuses work above `limit`, currently 96. Capacity Planning asked whether
that number is a safety limit or a cost limit, because the two imply different responses
to a refusal: a safety limit means shed load, a cost limit means queue and bill.

## Decision

Recorded as a cost limit at the time. **Superseded** by the later ruling that the
audit stage sheds rather than queues; this entry is kept because the reasoning is
cited in two audits and removing it would break those references.

## Consequences

- `docs/audit.md` states the current behaviour and is authoritative over this entry.
- No change to `DEFAULT_AUDIT_LIMIT`.
- The Delivery Engineering team owns the shed-count dashboard.
