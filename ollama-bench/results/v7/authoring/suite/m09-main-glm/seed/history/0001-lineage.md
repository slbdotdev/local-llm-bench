# 0001 - lineage: clarify the manifest limit

- Date: 2034-08-12
- Status: **accepted**
- Proposer: E. Thorsdottir (Client Integrations)

## Context

The lineage stage refuses work above `limit`, currently 250. Capacity Planning asked whether
that number is a safety limit or a cost limit, because the two imply different responses
to a refusal: a safety limit means shed load, a cost limit means queue and bill.

## Decision

It is a **safety limit**. The lineage stage sheds rather than queues, and `drain` is
responsible for reporting the shed count. The number itself is unchanged at 250.

## Consequences

- `docs/lineage.md` states the current behaviour and is authoritative over this entry.
- No change to `DEFAULT_LINEAGE_LIMIT`.
- The Client Integrations team owns the shed-count dashboard.
