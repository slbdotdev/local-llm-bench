# 0007 - throttle: re-scope the manifest limit

- Date: 2034-02-24
- Status: **superseded**
- Proposer: S. Nwachukwu (Platform Reliability)

## Context

The throttle stage refuses work above `limit`, currently 12. Capacity Planning asked whether
that number is a safety limit or a cost limit, because the two imply different responses
to a refusal: a safety limit means shed load, a cost limit means queue and bill.

## Decision

Recorded as a cost limit at the time. **Superseded** by the later ruling that the
throttle stage sheds rather than queues; this entry is kept because the reasoning is
cited in two audits and removing it would break those references.

## Consequences

- `docs/throttle.md` states the current behaviour and is authoritative over this entry.
- No change to `DEFAULT_THROTTLE_LIMIT`.
- The Platform Reliability team owns the shed-count dashboard.
