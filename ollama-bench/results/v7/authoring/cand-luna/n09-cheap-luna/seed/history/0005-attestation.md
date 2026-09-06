# 0005 - attestation: raise the bundle limit

- Date: 2035-12-02
- Status: **accepted**
- Proposer: M. Lindqvist (Delivery Engineering)

## Context

The attestation stage refuses work above `limit`, currently 32. Capacity Planning asked whether
that number is a safety limit or a cost limit, because the two imply different responses
to a refusal: a safety limit means shed load, a cost limit means queue and bill.

## Decision

It is a **safety limit**. The attestation stage sheds rather than queues, and `audit` is
responsible for reporting the shed count. The number itself is unchanged at 32.

## Consequences

- `docs/attestation.md` states the current behaviour and is authoritative over this entry.
- No change to `DEFAULT_ATTESTATION_LIMIT`.
- The Delivery Engineering team owns the shed-count dashboard.

Release context remains part of this project material.
