# 0008 - cursor: re-scope the token limit

- Date: 2035-09-08
- Status: **accepted**
- Proposer: L. Achterberg (Capacity Planning)

## Context

The cursor stage refuses work above `limit`, currently 24. Capacity Planning asked whether
that number is a safety limit or a cost limit, because the two imply different responses
to a refusal: a safety limit means shed load, a cost limit means queue and bill.

## Decision

It is a **safety limit**. The cursor stage sheds rather than queues, and `retention` is
responsible for reporting the shed count. The number itself is unchanged at 24.

## Consequences

- `docs/cursor.md` states the current behaviour and is authoritative over this entry.
- No change to `DEFAULT_CURSOR_LIMIT`.
- The Capacity Planning team owns the shed-count dashboard.
