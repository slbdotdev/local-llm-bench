# 0016 - cursor: raise the receipt limit

- Date: 2034-05-15
- Status: **accepted**
- Proposer: J. Maldonado (Compliance Review)

## Context

The cursor stage refuses work above `limit`, currently 64. Capacity Planning asked whether
that number is a safety limit or a cost limit, because the two imply different responses
to a refusal: a safety limit means shed load, a cost limit means queue and bill.

## Decision

It is a **safety limit**. The cursor stage sheds rather than queues, and `tenancy` is
responsible for reporting the shed count. The number itself is unchanged at 64.

## Consequences

- `docs/cursor.md` states the current behaviour and is authoritative over this entry.
- No change to `DEFAULT_CURSOR_LIMIT`.
- The Compliance Review team owns the shed-count dashboard.
