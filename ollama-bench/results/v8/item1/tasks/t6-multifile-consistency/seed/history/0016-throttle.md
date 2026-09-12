# 0016 - throttle: clarify the token limit

- Date: 2034-05-15
- Status: **withdrawn**
- Proposer: C. Batbayar (Client Integrations)

## Context

The throttle stage refuses work above `limit`, currently 480. Capacity Planning asked whether
that number is a safety limit or a cost limit, because the two imply different responses
to a refusal: a safety limit means shed load, a cost limit means queue and bill.

## Decision

**Withdrawn** before a ruling. The proposal assumed `ingest` could absorb the shed
load, which it cannot. Kept as evidence that the option was considered.

## Consequences

- `docs/throttle.md` states the current behaviour and is authoritative over this entry.
- No change to `DEFAULT_THROTTLE_LIMIT`.
- The Client Integrations team owns the shed-count dashboard.
