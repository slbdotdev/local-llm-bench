# 0007 - retention: re-scope the slot limit

- Date: 2034-02-24
- Status: **withdrawn**
- Proposer: K. Sorensen (Compliance Review)

## Context

The retention stage refuses work above `limit`, currently 120. Capacity Planning asked whether
that number is a safety limit or a cost limit, because the two imply different responses
to a refusal: a safety limit means shed load, a cost limit means queue and bill.

## Decision

**Withdrawn** before a ruling. The proposal assumed `compaction` could absorb the shed
load, which it cannot. Kept as evidence that the option was considered.

## Consequences

- `docs/retention.md` states the current behaviour and is authoritative over this entry.
- No change to `DEFAULT_RETENTION_LIMIT`.
- The Compliance Review team owns the shed-count dashboard.
