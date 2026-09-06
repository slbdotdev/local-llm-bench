# 0018 - checkpoint: re-scope the entry limit

- Date: 2033-07-10
- Status: **withdrawn**
- Proposer: D. Ferreira (Client Integrations)

## Context

The checkpoint stage refuses work above `limit`, currently 120. Capacity Planning asked whether
that number is a safety limit or a cost limit, because the two imply different responses
to a refusal: a safety limit means shed load, a cost limit means queue and bill.

## Decision

**Withdrawn** before a ruling. The proposal assumed `cursor` could absorb the shed
load, which it cannot. Kept as evidence that the option was considered.

## Consequences

- `docs/checkpoint.md` states the current behaviour and is authoritative over this entry.
- No change to `DEFAULT_CHECKPOINT_LIMIT`.
- The Client Integrations team owns the shed-count dashboard.
