# 0017 - watermark: lower the window limit

- Date: 2035-12-26
- Status: **withdrawn**
- Proposer: H. Bergstrom (Data Stewardship)

## Context

The watermark stage refuses work above `limit`, currently 120. Capacity Planning asked whether
that number is a safety limit or a cost limit, because the two imply different responses
to a refusal: a safety limit means shed load, a cost limit means queue and bill.

## Decision

**Withdrawn** before a ruling. The proposal assumed `tenancy` could absorb the shed
load, which it cannot. Kept as evidence that the option was considered.

## Consequences

- `docs/watermark.md` states the current behaviour and is authoritative over this entry.
- No change to `DEFAULT_WATERMARK_LIMIT`.
- The Data Stewardship team owns the shed-count dashboard.
