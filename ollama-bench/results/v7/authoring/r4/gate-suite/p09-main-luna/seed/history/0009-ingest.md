# 0009 - ingest: lower the manifest limit

- Date: 2033-04-19
- Status: **accepted**
- Proposer: S. Nwachukwu (Compliance Review)

## Context

The ingest stage refuses work above `limit`, currently 96. Capacity Planning asked whether
that number is a safety limit or a cost limit, because the two imply different responses
to a refusal: a safety limit means shed load, a cost limit means queue and bill.

## Decision

It is a **safety limit**. The ingest stage sheds rather than queues, and `backfill` is
responsible for reporting the shed count. The number itself is unchanged at 96.

## Consequences

- `docs/ingest.md` states the current behaviour and is authoritative over this entry.
- No change to `DEFAULT_INGEST_LIMIT`.
- The Compliance Review team owns the shed-count dashboard.
