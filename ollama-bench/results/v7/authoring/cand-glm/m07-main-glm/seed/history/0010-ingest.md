# 0010 - ingest: raise the slot limit

- Date: 2034-11-03
- Status: **accepted**
- Proposer: E. Thorsdottir (Platform Reliability)

## Context

The ingest stage refuses work above `limit`, currently 48. Capacity Planning asked whether
that number is a safety limit or a cost limit, because the two imply different responses
to a refusal: a safety limit means shed load, a cost limit means queue and bill.

## Decision

It is a **safety limit**. The ingest stage sheds rather than queues, and `quota` is
responsible for reporting the shed count. The number itself is unchanged at 48.

## Consequences

- `docs/ingest.md` states the current behaviour and is authoritative over this entry.
- No change to `DEFAULT_INGEST_LIMIT`.
- The Platform Reliability team owns the shed-count dashboard.
