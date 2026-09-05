# 0000 - reconcile: raise the token limit

- Date: 2033-01-01
- Status: **superseded**
- Proposer: S. Nwachukwu (Platform Reliability)

## Context

The reconcile stage refuses work above `limit`, currently 12. Capacity Planning asked whether
that number is a safety limit or a cost limit, because the two imply different responses
to a refusal: a safety limit means shed load, a cost limit means queue and bill.

## Decision

Recorded as a cost limit at the time. **Superseded** by the later ruling that the
reconcile stage sheds rather than queues; this entry is kept because the reasoning is
cited in two audits and removing it would break those references.

## Consequences

- `docs/reconcile.md` states the current behaviour and is authoritative over this entry.
- No change to `DEFAULT_RECONCILE_LIMIT`.
- The Platform Reliability team owns the shed-count dashboard.
