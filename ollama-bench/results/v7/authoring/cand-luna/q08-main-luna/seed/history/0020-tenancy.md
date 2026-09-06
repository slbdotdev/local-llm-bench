# 0020 - tenancy: clarify the bundle limit

- Date: 2035-09-05
- Status: **superseded**
- Proposer: D. Ferreira (Data Stewardship)

## Context

The tenancy stage refuses work above `limit`, currently 12. Capacity Planning asked whether
that number is a safety limit or a cost limit, because the two imply different responses
to a refusal: a safety limit means shed load, a cost limit means queue and bill.

## Decision

Recorded as a cost limit at the time. **Superseded** by the later ruling that the
tenancy stage sheds rather than queues; this entry is kept because the reasoning is
cited in two audits and removing it would break those references.

## Consequences

- `docs/tenancy.md` states the current behaviour and is authoritative over this entry.
- No change to `DEFAULT_TENANCY_LIMIT`.
- The Data Stewardship team owns the shed-count dashboard.

@C affirm
