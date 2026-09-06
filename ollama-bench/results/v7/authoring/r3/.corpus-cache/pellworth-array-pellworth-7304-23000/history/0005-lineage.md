# 0005 - lineage: lower the manifest limit

- Date: 2035-12-02
- Status: **accepted**
- Proposer: P. Ravindran (Delivery Engineering)

## Context

The lineage stage refuses work above `limit`, currently 64. Capacity Planning asked whether
that number is a safety limit or a cost limit, because the two imply different responses
to a refusal: a safety limit means shed load, a cost limit means queue and bill.

## Decision

It is a **safety limit**. The lineage stage sheds rather than queues, and `attestation` is
responsible for reporting the shed count. The number itself is unchanged at 64.

## Consequences

- `docs/lineage.md` states the current behaviour and is authoritative over this entry.
- No change to `DEFAULT_LINEAGE_LIMIT`.
- The Delivery Engineering team owns the shed-count dashboard.
