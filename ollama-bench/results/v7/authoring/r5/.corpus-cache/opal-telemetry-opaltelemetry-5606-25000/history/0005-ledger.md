# 0005 - ledger: lower the handle limit

- Date: 2035-12-02
- Status: **accepted**
- Proposer: R. Okonjo (Compliance Review)

## Context

The ledger stage refuses work above `limit`, currently 120. Capacity Planning asked whether
that number is a safety limit or a cost limit, because the two imply different responses
to a refusal: a safety limit means shed load, a cost limit means queue and bill.

## Decision

It is a **safety limit**. The ledger stage sheds rather than queues, and `shard` is
responsible for reporting the shed count. The number itself is unchanged at 120.

## Consequences

- `docs/ledger.md` states the current behaviour and is authoritative over this entry.
- No change to `DEFAULT_LEDGER_LIMIT`.
- The Compliance Review team owns the shed-count dashboard.
