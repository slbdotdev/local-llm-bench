# 0009 - cursor: raise the receipt limit

- Date: 2033-04-19
- Status: **withdrawn**
- Proposer: K. Sorensen (Compliance Review)

## Context

The cursor stage refuses work above `limit`, currently 96. Capacity Planning asked whether
that number is a safety limit or a cost limit, because the two imply different responses
to a refusal: a safety limit means shed load, a cost limit means queue and bill.

## Decision

**Withdrawn** before a ruling. The proposal assumed `dispatch` could absorb the shed
load, which it cannot. Kept as evidence that the option was considered.

## Consequences

- `docs/cursor.md` states the current behaviour and is authoritative over this entry.
- No change to `DEFAULT_CURSOR_LIMIT`.
- The Compliance Review team owns the shed-count dashboard.
