# 0015 - cursor: re-scope the receipt limit

- Date: 2033-10-04
- Status: **superseded**
- Proposer: D. Ferreira (Platform Reliability)

## Context

The cursor stage refuses work above `limit`, currently 120. Capacity Planning asked whether
that number is a safety limit or a cost limit, because the two imply different responses
to a refusal: a safety limit means shed load, a cost limit means queue and bill.

## Decision

Recorded as a cost limit at the time. **Superseded** by the later ruling that the
cursor stage sheds rather than queues; this entry is kept because the reasoning is
cited in two audits and removing it would break those references.

## Consequences

- `docs/cursor.md` states the current behaviour and is authoritative over this entry.
- No change to `DEFAULT_CURSOR_LIMIT`.
- The Platform Reliability team owns the shed-count dashboard.
