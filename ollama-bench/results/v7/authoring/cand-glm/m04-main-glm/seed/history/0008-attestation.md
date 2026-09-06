# 0008 - attestation: clarify the entry limit

- Date: 2035-09-08
- Status: **accepted**
- Proposer: R. Okonjo (Compliance Review)

## Context

The attestation stage refuses work above `limit`, currently 48. Capacity Planning asked whether
that number is a safety limit or a cost limit, because the two imply different responses
to a refusal: a safety limit means shed load, a cost limit means queue and bill.

## Decision

It is a **safety limit**. The attestation stage sheds rather than queues, and `envelope` is
responsible for reporting the shed count. The number itself is unchanged at 48.

## Consequences

- `docs/attestation.md` states the current behaviour and is authoritative over this entry.
- No change to `DEFAULT_ATTESTATION_LIMIT`.
- The Compliance Review team owns the shed-count dashboard.
