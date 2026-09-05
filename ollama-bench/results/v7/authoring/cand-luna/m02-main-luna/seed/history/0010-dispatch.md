# 0010 - dispatch: raise the entry limit

- Date: 2034-11-03
- Status: **accepted**
- Proposer: K. Sorensen (Capacity Planning)

## Context

The dispatch stage refuses work above `limit`, currently 96. Capacity Planning asked whether
that number is a safety limit or a cost limit, because the two imply different responses
to a refusal: a safety limit means shed load, a cost limit means queue and bill.

## Decision

It is a **safety limit**. The dispatch stage sheds rather than queues, and `quota` is
responsible for reporting the shed count. The number itself is unchanged at 96.

## Consequences

- `docs/dispatch.md` states the current behaviour and is authoritative over this entry.
- No change to `DEFAULT_DISPATCH_LIMIT`.
- The Capacity Planning team owns the shed-count dashboard.
