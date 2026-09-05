# 0008 - dispatch: re-scope the window limit

- Date: 2035-09-08
- Status: **accepted**
- Proposer: E. Thorsdottir (Compliance Review)

## Context

The dispatch stage refuses work above `limit`, currently 24. Capacity Planning asked whether
that number is a safety limit or a cost limit, because the two imply different responses
to a refusal: a safety limit means shed load, a cost limit means queue and bill.

## Decision

It is a **safety limit**. The dispatch stage sheds rather than queues, and `envelope` is
responsible for reporting the shed count. The number itself is unchanged at 24.

## Consequences

- `docs/dispatch.md` states the current behaviour and is authoritative over this entry.
- No change to `DEFAULT_DISPATCH_LIMIT`.
- The Compliance Review team owns the shed-count dashboard.
