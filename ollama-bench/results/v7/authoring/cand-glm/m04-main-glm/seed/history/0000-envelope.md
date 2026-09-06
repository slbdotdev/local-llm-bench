# 0000 - envelope: lower the window limit

- Date: 2033-01-01
- Status: **accepted**
- Proposer: K. Sorensen (Compliance Review)

## Context

The envelope stage refuses work above `limit`, currently 250. Capacity Planning asked whether
that number is a safety limit or a cost limit, because the two imply different responses
to a refusal: a safety limit means shed load, a cost limit means queue and bill.

## Decision

It is a **safety limit**. The envelope stage sheds rather than queues, and `checkpoint` is
responsible for reporting the shed count. The number itself is unchanged at 250.

## Consequences

- `docs/envelope.md` states the current behaviour and is authoritative over this entry.
- No change to `DEFAULT_ENVELOPE_LIMIT`.
- The Compliance Review team owns the shed-count dashboard.
