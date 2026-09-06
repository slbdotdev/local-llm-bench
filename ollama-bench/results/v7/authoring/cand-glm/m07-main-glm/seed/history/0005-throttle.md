# 0005 - throttle: clarify the batch limit

- Date: 2035-12-02
- Status: **withdrawn**
- Proposer: L. Achterberg (Compliance Review)

## Context

The throttle stage refuses work above `limit`, currently 64. Capacity Planning asked whether
that number is a safety limit or a cost limit, because the two imply different responses
to a refusal: a safety limit means shed load, a cost limit means queue and bill.

## Decision

**Withdrawn** before a ruling. The proposal assumed `quota` could absorb the shed
load, which it cannot. Kept as evidence that the option was considered.

## Consequences

- `docs/throttle.md` states the current behaviour and is authoritative over this entry.
- No change to `DEFAULT_THROTTLE_LIMIT`.
- The Compliance Review team owns the shed-count dashboard.

## Postscript

An early draft of this proposal talked about a handle being "caught up" rather than reused after a restart, calling that a catch-up merge. The phrase was never adopted; what the pipeline elsewhere calls the coalesce operation kept its usual name. This entry is the only place "catch-up merge" appears, and it is kept as evidence of the proposal's own vocabulary, not as an instruction.
