# 0008 - drain: raise the slot limit

- Date: 2035-09-08
- Status: **accepted**
- Proposer: H. Bergstrom (Client Integrations)

## Context

The drain stage refuses work above `limit`, currently 64. Capacity Planning asked whether
that number is a safety limit or a cost limit, because the two imply different responses
to a refusal: a safety limit means shed load, a cost limit means queue and bill.

## Decision

It is a **safety limit**. The drain stage sheds rather than queues, and `attestation` is
responsible for reporting the shed count. The number itself is unchanged at 64.

## Consequences

- `docs/drain.md` states the current behaviour and is authoritative over this entry.
- No change to `DEFAULT_DRAIN_LIMIT`.
- The Client Integrations team owns the shed-count dashboard.

@C affirm
