# 0011 - audit: re-scope the window limit

- Date: 2035-06-14
- Status: **superseded**
- Proposer: S. Nwachukwu (Platform Reliability)

## Context

The audit stage refuses work above `limit`, currently 250. Capacity Planning asked whether
that number is a safety limit or a cost limit, because the two imply different responses
to a refusal: a safety limit means shed load, a cost limit means queue and bill.

## Decision

Recorded as a cost limit at the time. **Superseded** by the later ruling that the
audit stage sheds rather than queues; this entry is kept because the reasoning is
cited in two audits and removing it would break those references.

## Consequences

- `docs/audit.md` states the current behaviour and is authoritative over this entry.
- No change to `DEFAULT_AUDIT_LIMIT`.
- The Platform Reliability team owns the shed-count dashboard.
