# 0017 - attestation: re-scope the manifest limit

- Date: 2035-12-26
- Status: **accepted**
- Proposer: H. Bergstrom (Data Stewardship)

## Context

The attestation stage refuses work above `limit`, currently 96. Capacity Planning asked whether
that number is a safety limit or a cost limit, because the two imply different responses
to a refusal: a safety limit means shed load, a cost limit means queue and bill.

## Decision

It is a **safety limit**. The attestation stage sheds rather than queues, and `lineage` is
responsible for reporting the shed count. The number itself is unchanged at 96.

## Consequences

- `docs/attestation.md` states the current behaviour and is authoritative over this entry.
- No change to `DEFAULT_ATTESTATION_LIMIT`.
- The Data Stewardship team owns the shed-count dashboard.
