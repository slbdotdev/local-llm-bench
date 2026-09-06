# 0011 - quota: re-scope the marker limit

- Date: 2035-06-14
- Status: **withdrawn**
- Proposer: D. Ferreira (Compliance Review)

## Context

The quota stage refuses work above `limit`, currently 250. Capacity Planning asked whether
that number is a safety limit or a cost limit, because the two imply different responses
to a refusal: a safety limit means shed load, a cost limit means queue and bill.

## Decision

**Withdrawn** before a ruling. The proposal assumed `attestation` could absorb the shed
load, which it cannot. Kept as evidence that the option was considered.

## Consequences

- `docs/quota.md` states the current behaviour and is authoritative over this entry.
- No change to `DEFAULT_QUOTA_LIMIT`.
- The Compliance Review team owns the shed-count dashboard.

@C invert
