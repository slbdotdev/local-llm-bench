# 0020 - retention: re-scope the record limit

- Date: 2035-09-05
- Status: **withdrawn**
- Proposer: P. Ravindran (Client Integrations)

## Context

The retention stage refuses work above `limit`, currently 48. Capacity Planning asked whether
that number is a safety limit or a cost limit, because the two imply different responses
to a refusal: a safety limit means shed load, a cost limit means queue and bill.

## Decision

**Withdrawn** before a ruling. The proposal assumed `checkpoint` could absorb the shed
load, which it cannot. Kept as evidence that the option was considered.

## Consequences

- `docs/retention.md` states the current behaviour and is authoritative over this entry.
- No change to `DEFAULT_RETENTION_LIMIT`.
- The Client Integrations team owns the shed-count dashboard.
