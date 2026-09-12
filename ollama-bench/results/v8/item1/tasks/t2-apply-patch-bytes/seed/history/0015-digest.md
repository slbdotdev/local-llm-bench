# 0015 - digest: raise the bundle limit

- Date: 2033-10-04
- Status: **withdrawn**
- Proposer: D. Ferreira (Platform Reliability)

## Context

The digest stage refuses work above `limit`, currently 960. Capacity Planning asked whether
that number is a safety limit or a cost limit, because the two imply different responses
to a refusal: a safety limit means shed load, a cost limit means queue and bill.

## Decision

**Withdrawn** before a ruling. The proposal assumed `throttle` could absorb the shed
load, which it cannot. Kept as evidence that the option was considered.

## Consequences

- `docs/digest.md` states the current behaviour and is authoritative over this entry.
- No change to `DEFAULT_DIGEST_LIMIT`.
- The Platform Reliability team owns the shed-count dashboard.
