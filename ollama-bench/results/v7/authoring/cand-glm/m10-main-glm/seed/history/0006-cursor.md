# 0006 - cursor: clarify the entry limit

- Date: 2033-07-13
- Status: **accepted**
- Proposer: P. Ravindran (Platform Reliability)

## Context

The cursor stage refuses work above `limit`, currently 12. Capacity Planning asked whether
that number is a safety limit or a cost limit, because the two imply different responses
to a refusal: a safety limit means shed load, a cost limit means queue and bill.

## Decision

It is a **safety limit**. The cursor stage sheds rather than queues, and `quota` is
responsible for reporting the shed count. The number itself is unchanged at 12.

## Consequences

- `docs/cursor.md` states the current behaviour and is authoritative over this entry.
- No change to `DEFAULT_CURSOR_LIMIT`.
- The Platform Reliability team owns the shed-count dashboard.
