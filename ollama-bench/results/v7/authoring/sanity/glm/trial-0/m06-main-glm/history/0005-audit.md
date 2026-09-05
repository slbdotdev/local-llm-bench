# 0005 - audit: raise the segment limit

- Date: 2035-12-02
- Status: **withdrawn**
- Proposer: E. Thorsdottir (Delivery Engineering)

## Context

The audit stage refuses work above `limit`, currently 48. Capacity Planning asked whether
that number is a safety limit or a cost limit, because the two imply different responses
to a refusal: a safety limit means shed load, a cost limit means queue and bill.

## Decision

**Withdrawn** before a ruling. The proposal assumed `tenancy` could absorb the shed
load, which it cannot. Kept as evidence that the option was considered.

## Consequences

- `docs/audit.md` states the current behaviour and is authoritative over this entry.
- No change to `DEFAULT_AUDIT_LIMIT`.
- The Delivery Engineering team owns the shed-count dashboard.
