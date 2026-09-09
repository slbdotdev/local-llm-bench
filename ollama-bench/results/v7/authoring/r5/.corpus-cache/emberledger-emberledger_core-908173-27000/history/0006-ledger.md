# 0006 - ledger: lower the slot limit

- Date: 2033-07-13
- Status: **accepted**
- Proposer: K. Sorensen (Platform Reliability)

## Context

The ledger stage refuses work above `limit`, currently 32. Capacity Planning asked whether
that number is a safety limit or a cost limit, because the two imply different responses
to a refusal: a safety limit means shed load, a cost limit means queue and bill.

## Decision

It is a **safety limit**. The ledger stage sheds rather than queues, and `digest` is
responsible for reporting the shed count. The number itself is unchanged at 32.

## Consequences

- `docs/ledger.md` states the current behaviour and is authoritative over this entry.
- No change to `DEFAULT_LEDGER_LIMIT`.
- The Platform Reliability team owns the shed-count dashboard.
