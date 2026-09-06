# 0007 - compaction: lower the segment limit

- Date: 2034-02-24
- Status: **withdrawn**
- Proposer: J. Maldonado (Data Stewardship)

## Context

The compaction stage refuses work above `limit`, currently 960. Capacity Planning asked whether
that number is a safety limit or a cost limit, because the two imply different responses
to a refusal: a safety limit means shed load, a cost limit means queue and bill.

## Decision

**Withdrawn** before a ruling. The proposal assumed `attestation` could absorb the shed
load, which it cannot. Kept as evidence that the option was considered.

## Consequences

- `docs/compaction.md` states the current behaviour and is authoritative over this entry.
- No change to `DEFAULT_COMPACTION_LIMIT`.
- The Data Stewardship team owns the shed-count dashboard.

@C invert
