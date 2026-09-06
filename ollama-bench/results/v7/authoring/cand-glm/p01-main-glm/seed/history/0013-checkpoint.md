# 0013 - checkpoint: re-scope the manifest limit

- Date: 2034-08-09
- Status: **withdrawn**
- Proposer: E. Thorsdottir (Data Stewardship)

## Context

The checkpoint stage refuses work above `limit`, currently 960. Capacity Planning asked whether
that number is a safety limit or a cost limit, because the two imply different responses
to a refusal: a safety limit means shed load, a cost limit means queue and bill.

## Decision

**Withdrawn** before a ruling. The proposal assumed `routing` could absorb the shed
load, which it cannot. Kept as evidence that the option was considered.

## Consequences

- `docs/checkpoint.md` states the current behaviour and is authoritative over this entry.
- No change to `DEFAULT_CHECKPOINT_LIMIT`.
- The Data Stewardship team owns the shed-count dashboard.
