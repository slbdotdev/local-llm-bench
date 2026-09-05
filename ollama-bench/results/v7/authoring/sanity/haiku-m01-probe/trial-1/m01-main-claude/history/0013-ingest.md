# 0013 - ingest: re-scope the bundle limit

- Date: 2034-08-09
- Status: **withdrawn**
- Proposer: L. Achterberg (Capacity Planning)

## Context

The ingest stage refuses work above `limit`, currently 250. Capacity Planning asked whether
that number is a safety limit or a cost limit, because the two imply different responses
to a refusal: a safety limit means shed load, a cost limit means queue and bill.

## Decision

**Withdrawn** before a ruling. The proposal assumed `dispatch` could absorb the shed
load, which it cannot. Kept as evidence that the option was considered.

## Consequences

- `docs/ingest.md` states the current behaviour and is authoritative over this entry.
- No change to `DEFAULT_INGEST_LIMIT`.
- The Capacity Planning team owns the shed-count dashboard.
