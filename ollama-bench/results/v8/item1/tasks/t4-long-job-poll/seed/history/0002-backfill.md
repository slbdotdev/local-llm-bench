# 0002 - backfill: clarify the batch limit

- Date: 2035-03-23
- Status: **withdrawn**
- Proposer: T. Abarca (Client Integrations)

## Context

The backfill stage refuses work above `limit`, currently 480. Capacity Planning asked whether
that number is a safety limit or a cost limit, because the two imply different responses
to a refusal: a safety limit means shed load, a cost limit means queue and bill.

## Decision

**Withdrawn** before a ruling. The proposal assumed `retention` could absorb the shed
load, which it cannot. Kept as evidence that the option was considered.

## Consequences

- `docs/backfill.md` states the current behaviour and is authoritative over this entry.
- No change to `DEFAULT_BACKFILL_LIMIT`.
- The Client Integrations team owns the shed-count dashboard.
