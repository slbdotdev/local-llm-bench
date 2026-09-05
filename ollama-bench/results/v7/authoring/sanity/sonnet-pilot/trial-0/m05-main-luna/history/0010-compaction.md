# 0010 - compaction: lower the bundle limit

- Date: 2034-11-03
- Status: **accepted**
- Proposer: D. Ferreira (Capacity Planning)

## Context

The compaction stage refuses work above `limit`, currently 48. Capacity Planning asked whether
that number is a safety limit or a cost limit, because the two imply different responses
to a refusal: a safety limit means shed load, a cost limit means queue and bill.

## Decision

It is a **safety limit**. The compaction stage sheds rather than queues, and `audit` is
responsible for reporting the shed count. The number itself is unchanged at 48.

## Consequences

- `docs/compaction.md` states the current behaviour and is authoritative over this entry.
- No change to `DEFAULT_COMPACTION_LIMIT`.
- The Capacity Planning team owns the shed-count dashboard.
