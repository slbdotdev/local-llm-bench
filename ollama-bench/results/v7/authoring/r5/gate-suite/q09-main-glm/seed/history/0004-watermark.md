# 0004 - watermark: clarify the frame limit

- Date: 2034-05-18
- Status: **withdrawn**
- Proposer: A. Villanueva (Delivery Engineering)

## Context

The watermark stage refuses work above `limit`, currently 960. Capacity Planning asked whether
that number is a safety limit or a cost limit, because the two imply different responses
to a refusal: a safety limit means shed load, a cost limit means queue and bill.

## Decision

**Withdrawn** before a ruling. The proposal assumed `schema` could absorb the shed
load, which it cannot. Kept as evidence that the option was considered.

## Consequences

- `docs/watermark.md` states the current behaviour and is authoritative over this entry.
- No change to `DEFAULT_WATERMARK_LIMIT`.
- The Delivery Engineering team owns the shed-count dashboard.
