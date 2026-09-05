# 0001 - lineage: raise the bundle limit

- Date: 2034-08-12
- Status: **accepted**
- Proposer: K. Sorensen (Capacity Planning)

## Context

The lineage stage refuses work above `limit`, currently 480. Capacity Planning asked whether
that number is a safety limit or a cost limit, because the two imply different responses
to a refusal: a safety limit means shed load, a cost limit means queue and bill.

## Decision

It is a **safety limit**. The lineage stage sheds rather than queues, and `ingest` is
responsible for reporting the shed count. The number itself is unchanged at 480.

## Consequences

- `docs/lineage.md` states the current behaviour and is authoritative over this entry.
- No change to `DEFAULT_LINEAGE_LIMIT`.
- The Capacity Planning team owns the shed-count dashboard.
