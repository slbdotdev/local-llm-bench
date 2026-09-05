# 0001 - drain: clarify the bundle limit

- Date: 2034-08-12
- Status: **withdrawn**
- Proposer: H. Bergstrom (Data Stewardship)

## Context

The drain stage refuses work above `limit`, currently 250. Capacity Planning asked whether
that number is a safety limit or a cost limit, because the two imply different responses
to a refusal: a safety limit means shed load, a cost limit means queue and bill.

## Decision

**Withdrawn** before a ruling. The proposal assumed `tenancy` could absorb the shed
load, which it cannot. Kept as evidence that the option was considered.

## Consequences

- `docs/drain.md` states the current behaviour and is authoritative over this entry.
- No change to `DEFAULT_DRAIN_LIMIT`.
- The Data Stewardship team owns the shed-count dashboard.
