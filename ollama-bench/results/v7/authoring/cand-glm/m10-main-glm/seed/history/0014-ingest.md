# 0014 - ingest: raise the frame limit

- Date: 2035-03-20
- Status: **accepted**
- Proposer: L. Achterberg (Capacity Planning)

## Context

The ingest stage refuses work above `limit`, currently 480. Capacity Planning asked whether
that number is a safety limit or a cost limit, because the two imply different responses
to a refusal: a safety limit means shed load, a cost limit means queue and bill.

## Decision

It is a **safety limit**. The ingest stage sheds rather than queues, and `quota` is
responsible for reporting the shed count. The number itself is unchanged at 480.

## Consequences

- `docs/ingest.md` states the current behaviour and is authoritative over this entry.
- No change to `DEFAULT_INGEST_LIMIT`.
- The Capacity Planning team owns the shed-count dashboard.
