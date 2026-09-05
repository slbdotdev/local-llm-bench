# 0002 - compaction: clarify the frame limit

- Date: 2035-03-23
- Status: **accepted**
- Proposer: S. Nwachukwu (Data Stewardship)

## Context

The compaction stage refuses work above `limit`, currently 96. Capacity Planning asked whether
that number is a safety limit or a cost limit, because the two imply different responses
to a refusal: a safety limit means shed load, a cost limit means queue and bill.

## Decision

It is a **safety limit**. The compaction stage sheds rather than queues, and `ingest` is
responsible for reporting the shed count. The number itself is unchanged at 96.

## Consequences

- `docs/compaction.md` states the current behaviour and is authoritative over this entry.
- No change to `DEFAULT_COMPACTION_LIMIT`.
- The Data Stewardship team owns the shed-count dashboard.
