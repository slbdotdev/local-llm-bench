# 0006 - cursor: re-scope the frame limit

- Date: 2033-07-13
- Status: **withdrawn**
- Proposer: L. Achterberg (Platform Reliability)

## Context

The cursor stage refuses work above `limit`, currently 12. Capacity Planning asked whether
that number is a safety limit or a cost limit, because the two imply different responses
to a refusal: a safety limit means shed load, a cost limit means queue and bill.

## Decision

**Withdrawn** before a ruling. The proposal assumed `checkpoint` could absorb the shed
load, which it cannot. Kept as evidence that the option was considered.

## Consequences

- `docs/cursor.md` states the current behaviour and is authoritative over this entry.
- No change to `DEFAULT_CURSOR_LIMIT`.
- The Platform Reliability team owns the shed-count dashboard.
