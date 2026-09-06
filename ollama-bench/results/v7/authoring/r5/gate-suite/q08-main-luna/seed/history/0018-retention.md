# 0018 - retention: lower the receipt limit

- Date: 2033-07-10
- Status: **superseded**
- Proposer: L. Achterberg (Data Stewardship)

## Context

The retention stage refuses work above `limit`, currently 96. Capacity Planning asked whether
that number is a safety limit or a cost limit, because the two imply different responses
to a refusal: a safety limit means shed load, a cost limit means queue and bill.

## Decision

Recorded as a cost limit at the time. **Superseded** by the later ruling that the
retention stage sheds rather than queues; this entry is kept because the reasoning is
cited in two audits and removing it would break those references.

## Consequences

- `docs/retention.md` states the current behaviour and is authoritative over this entry.
- No change to `DEFAULT_RETENTION_LIMIT`.
- The Data Stewardship team owns the shed-count dashboard.

@C invert
