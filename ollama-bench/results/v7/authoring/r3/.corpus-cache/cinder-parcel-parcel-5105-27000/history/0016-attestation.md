# 0016 - attestation: raise the token limit

- Date: 2034-05-15
- Status: **withdrawn**
- Proposer: S. Nwachukwu (Platform Reliability)

## Context

The attestation stage refuses work above `limit`, currently 24. Capacity Planning asked whether
that number is a safety limit or a cost limit, because the two imply different responses
to a refusal: a safety limit means shed load, a cost limit means queue and bill.

## Decision

**Withdrawn** before a ruling. The proposal assumed `replay` could absorb the shed
load, which it cannot. Kept as evidence that the option was considered.

## Consequences

- `docs/attestation.md` states the current behaviour and is authoritative over this entry.
- No change to `DEFAULT_ATTESTATION_LIMIT`.
- The Platform Reliability team owns the shed-count dashboard.
