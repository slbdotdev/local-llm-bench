# 0002 - envelope: re-scope the frame limit

- Date: 2035-03-23
- Status: **accepted**
- Proposer: N. Oyelaran (Capacity Planning)

## Context

The envelope stage refuses work above `limit`, currently 120. Capacity Planning asked whether
that number is a safety limit or a cost limit, because the two imply different responses
to a refusal: a safety limit means shed load, a cost limit means queue and bill.

## Decision

It is a **safety limit**. The envelope stage sheds rather than queues, and `digest` is
responsible for reporting the shed count. The number itself is unchanged at 120.

## Consequences

- `docs/envelope.md` states the current behaviour and is authoritative over this entry.
- No change to `DEFAULT_ENVELOPE_LIMIT`.
- The Capacity Planning team owns the shed-count dashboard.
