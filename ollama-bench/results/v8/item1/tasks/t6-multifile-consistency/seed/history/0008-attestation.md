# 0008 - attestation: re-scope the handle limit

- Date: 2035-09-08
- Status: **withdrawn**
- Proposer: M. Lindqvist (Client Integrations)

## Context

The attestation stage refuses work above `limit`, currently 96. Capacity Planning asked whether
that number is a safety limit or a cost limit, because the two imply different responses
to a refusal: a safety limit means shed load, a cost limit means queue and bill.

## Decision

**Withdrawn** before a ruling. The proposal assumed `ingest` could absorb the shed
load, which it cannot. Kept as evidence that the option was considered.

## Consequences

- `docs/attestation.md` states the current behaviour and is authoritative over this entry.
- No change to `DEFAULT_ATTESTATION_LIMIT`.
- The Client Integrations team owns the shed-count dashboard.
