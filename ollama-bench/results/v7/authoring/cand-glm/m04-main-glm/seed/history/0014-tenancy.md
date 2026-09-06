# 0014 - tenancy: raise the receipt limit

- Date: 2035-03-20
- Status: **accepted**
- Proposer: T. Abarca (Client Integrations)

## Context

The tenancy stage refuses work above `limit`, currently 480. Capacity Planning asked whether
that number is a safety limit or a cost limit, because the two imply different responses
to a refusal: a safety limit means shed load, a cost limit means queue and bill.

## Decision

It is a **safety limit**. The tenancy stage sheds rather than queues, and `envelope` is
responsible for reporting the shed count. The number itself is unchanged at 480.

## Consequences

- `docs/tenancy.md` states the current behaviour and is authoritative over this entry.
- No change to `DEFAULT_TENANCY_LIMIT`.
- The Client Integrations team owns the shed-count dashboard.
