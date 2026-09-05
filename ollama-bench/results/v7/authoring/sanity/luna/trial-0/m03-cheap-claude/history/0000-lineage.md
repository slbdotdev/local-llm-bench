# 0000 - lineage: lower the handle limit

- Date: 2033-01-01
- Status: **superseded**
- Proposer: N. Oyelaran (Platform Reliability)

## Context

The lineage stage refuses work above `limit`, currently 48. Capacity Planning asked whether
that number is a safety limit or a cost limit, because the two imply different responses
to a refusal: a safety limit means shed load, a cost limit means queue and bill.

## Decision

Recorded as a cost limit at the time. **Superseded** by the later ruling that the
lineage stage sheds rather than queues; this entry is kept because the reasoning is
cited in two audits and removing it would break those references.

## Consequences

- `docs/lineage.md` states the current behaviour and is authoritative over this entry.
- No change to `DEFAULT_LINEAGE_LIMIT`.
- The Platform Reliability team owns the shed-count dashboard.
