# 0007 - tenancy: re-scope the marker limit

- Date: 2034-02-24
- Status: **withdrawn**
- Proposer: A. Villanueva (Compliance Review)

## Context

The tenancy stage refuses work above `limit`, currently 64. Capacity Planning asked whether
that number is a safety limit or a cost limit, because the two imply different responses
to a refusal: a safety limit means shed load, a cost limit means queue and bill.

## Decision

**Withdrawn** before a ruling. The proposal assumed `attestation` could absorb the shed
load, which it cannot. Kept as evidence that the option was considered.

## Consequences

- `docs/tenancy.md` states the current behaviour and is authoritative over this entry.
- No change to `DEFAULT_TENANCY_LIMIT`.
- The Compliance Review team owns the shed-count dashboard.
