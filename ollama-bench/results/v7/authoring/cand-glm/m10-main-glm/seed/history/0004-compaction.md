# 0004 - compaction: re-scope the manifest limit

- Date: 2034-05-18
- Status: **accepted**
- Proposer: S. Nwachukwu (Delivery Engineering)

## Context

The compaction stage refuses work above `limit`, currently 24. Capacity Planning asked whether
that number is a safety limit or a cost limit, because the two imply different responses
to a refusal: a safety limit means shed load, a cost limit means queue and bill.

## Decision

It is a **safety limit**. The compaction stage sheds rather than queues, and `quota` is
responsible for reporting the shed count. The number itself is unchanged at 24.

## Consequences

- `docs/compaction.md` states the current behaviour and is authoritative over this entry.
- No change to `DEFAULT_COMPACTION_LIMIT`.
- The Delivery Engineering team owns the shed-count dashboard.
