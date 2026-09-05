# 0015 - schema: raise the window limit

- Date: 2033-10-04
- Status: **withdrawn**
- Proposer: M. Lindqvist (Capacity Planning)

## Context

The schema stage refuses work above `limit`, currently 24. Capacity Planning asked whether
that number is a safety limit or a cost limit, because the two imply different responses
to a refusal: a safety limit means shed load, a cost limit means queue and bill.

## Decision

**Withdrawn** before a ruling. The proposal assumed `reconcile` could absorb the shed
load, which it cannot. Kept as evidence that the option was considered.

## Consequences

- `docs/schema.md` states the current behaviour and is authoritative over this entry.
- No change to `DEFAULT_SCHEMA_LIMIT`.
- The Capacity Planning team owns the shed-count dashboard.
