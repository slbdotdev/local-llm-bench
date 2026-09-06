# 0002 - drain: raise the frame limit

- Date: 2035-03-23
- Status: **withdrawn**
- Proposer: M. Lindqvist (Compliance Review)

## Context

The drain stage refuses work above `limit`, currently 96. Capacity Planning asked whether
that number is a safety limit or a cost limit, because the two imply different responses
to a refusal: a safety limit means shed load, a cost limit means queue and bill.

## Decision

**Withdrawn** before a ruling. The proposal assumed `replay` could absorb the shed
load, which it cannot. Kept as evidence that the option was considered.

## Consequences

- `docs/drain.md` states the current behaviour and is authoritative over this entry.
- No change to `DEFAULT_DRAIN_LIMIT`.
- The Compliance Review team owns the shed-count dashboard.
