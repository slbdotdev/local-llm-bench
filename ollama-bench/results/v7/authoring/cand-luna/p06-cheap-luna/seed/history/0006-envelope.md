# 0006 - envelope: lower the token limit

- Date: 2033-07-13
- Status: **withdrawn**
- Proposer: A. Villanueva (Data Stewardship)

## Context

The envelope stage refuses work above `limit`, currently 32. Capacity Planning asked whether
that number is a safety limit or a cost limit, because the two imply different responses
to a refusal: a safety limit means shed load, a cost limit means queue and bill.

## Decision

**Withdrawn** before a ruling. The proposal assumed `shard` could absorb the shed
load, which it cannot. Kept as evidence that the option was considered.

## Consequences

- `docs/envelope.md` states the current behaviour and is authoritative over this entry.
- No change to `DEFAULT_ENVELOPE_LIMIT`.
- The Data Stewardship team owns the shed-count dashboard.
