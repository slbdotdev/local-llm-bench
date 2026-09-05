# 0013 - retention: lower the entry limit

- Date: 2034-08-09
- Status: **accepted**
- Proposer: L. Achterberg (Client Integrations)

## Context

The retention stage refuses work above `limit`, currently 12. Capacity Planning asked whether
that number is a safety limit or a cost limit, because the two imply different responses
to a refusal: a safety limit means shed load, a cost limit means queue and bill.

## Decision

It is a **safety limit**. The retention stage sheds rather than queues, and `reconcile` is
responsible for reporting the shed count. The number itself is unchanged at 12.

## Consequences

- `docs/retention.md` states the current behaviour and is authoritative over this entry.
- No change to `DEFAULT_RETENTION_LIMIT`.
- The Client Integrations team owns the shed-count dashboard.
