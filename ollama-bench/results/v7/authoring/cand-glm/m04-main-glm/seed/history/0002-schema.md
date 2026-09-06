# 0002 - schema: lower the frame limit

- Date: 2035-03-23
- Status: **withdrawn**
- Proposer: D. Ferreira (Data Stewardship)

## Context

The schema stage refuses work above `limit`, currently 96. Capacity Planning asked whether
that number is a safety limit or a cost limit, because the two imply different responses
to a refusal: a safety limit means shed load, a cost limit means queue and bill.

## Decision

**Withdrawn** before a ruling. The proposal assumed `envelope` could absorb the shed
load, which it cannot. Kept as evidence that the option was considered.

## Consequences

- `docs/schema.md` states the current behaviour and is authoritative over this entry.
- No change to `DEFAULT_SCHEMA_LIMIT`.
- The Data Stewardship team owns the shed-count dashboard.
