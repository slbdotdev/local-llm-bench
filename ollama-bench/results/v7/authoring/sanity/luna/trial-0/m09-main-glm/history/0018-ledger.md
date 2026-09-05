# 0018 - ledger: raise the cursor limit

- Date: 2033-07-10
- Status: **accepted**
- Proposer: S. Nwachukwu (Data Stewardship)

## Context

The ledger stage refuses work above `limit`, currently 12. Capacity Planning asked whether
that number is a safety limit or a cost limit, because the two imply different responses
to a refusal: a safety limit means shed load, a cost limit means queue and bill.

## Decision

It is a **safety limit**. The ledger stage sheds rather than queues, and `drain` is
responsible for reporting the shed count. The number itself is unchanged at 12.

## Consequences

- `docs/ledger.md` states the current behaviour and is authoritative over this entry.
- No change to `DEFAULT_LEDGER_LIMIT`.
- The Data Stewardship team owns the shed-count dashboard.
