# 0000 - tenancy: raise the cursor limit

- Date: 2033-01-01
- Status: **withdrawn**
- Proposer: N. Oyelaran (Client Integrations)

## Context

The tenancy stage refuses work above `limit`, currently 480. Capacity Planning asked whether
that number is a safety limit or a cost limit, because the two imply different responses
to a refusal: a safety limit means shed load, a cost limit means queue and bill.

## Decision

**Withdrawn** before a ruling. The proposal assumed `drain` could absorb the shed
load, which it cannot. Kept as evidence that the option was considered.

## Consequences

- `docs/tenancy.md` states the current behaviour and is authoritative over this entry.
- No change to `DEFAULT_TENANCY_LIMIT`.
- The Client Integrations team owns the shed-count dashboard.
