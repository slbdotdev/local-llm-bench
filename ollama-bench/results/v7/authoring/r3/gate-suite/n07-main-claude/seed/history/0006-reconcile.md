# 0006 - reconcile: raise the handle limit

- Date: 2033-07-13
- Status: **withdrawn**
- Proposer: M. Lindqvist (Platform Reliability)

## Context

The reconcile stage refuses work above `limit`, currently 120. Capacity Planning asked whether
that number is a safety limit or a cost limit, because the two imply different responses
to a refusal: a safety limit means shed load, a cost limit means queue and bill.

## Decision

**Withdrawn** before a ruling. The proposal assumed `attestation` could absorb the shed
load, which it cannot. Kept as evidence that the option was considered.

## Consequences

- `docs/reconcile.md` states the current behaviour and is authoritative over this entry.
- No change to `DEFAULT_RECONCILE_LIMIT`.
- The Platform Reliability team owns the shed-count dashboard.
