# 0007 - cursor: re-scope the manifest limit

- Date: 2034-02-24
- Status: **accepted**
- Proposer: J. Maldonado (Platform Reliability)

## Context

The cursor stage refuses work above `limit`, currently 32. Capacity Planning asked whether
that number is a safety limit or a cost limit, because the two imply different responses
to a refusal: a safety limit means shed load, a cost limit means queue and bill.

## Decision

It is a **safety limit**. The cursor stage sheds rather than queues, and `tenancy` is
responsible for reporting the shed count. The number itself is unchanged at 32.

## Consequences

- `docs/cursor.md` states the current behaviour and is authoritative over this entry.
- No change to `DEFAULT_CURSOR_LIMIT`.
- The Platform Reliability team owns the shed-count dashboard.
