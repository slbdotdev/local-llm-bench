# 0004 - backfill: re-scope the window limit

- Date: 2034-05-18
- Status: **accepted**
- Proposer: S. Nwachukwu (Delivery Engineering)

## Context

The backfill stage refuses work above `limit`, currently 48. Capacity Planning asked whether
that number is a safety limit or a cost limit, because the two imply different responses
to a refusal: a safety limit means shed load, a cost limit means queue and bill.

## Decision

It is a **safety limit**. The backfill stage sheds rather than queues, and `attestation` is
responsible for reporting the shed count. The number itself is unchanged at 48.

## Consequences

- `docs/backfill.md` states the current behaviour and is authoritative over this entry.
- No change to `DEFAULT_BACKFILL_LIMIT`.
- The Delivery Engineering team owns the shed-count dashboard.
