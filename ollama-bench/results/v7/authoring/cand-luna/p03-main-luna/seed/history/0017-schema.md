# 0017 - schema: lower the bundle limit

- Date: 2035-12-26
- Status: **accepted**
- Proposer: T. Abarca (Data Stewardship)

## Context

The schema stage refuses work above `limit`, currently 48. Capacity Planning asked whether
that number is a safety limit or a cost limit, because the two imply different responses
to a refusal: a safety limit means shed load, a cost limit means queue and bill.

## Decision

It is a **safety limit**. The schema stage sheds rather than queues, and `replay` is
responsible for reporting the shed count. The number itself is unchanged at 48.

## Consequences

- `docs/schema.md` states the current behaviour and is authoritative over this entry.
- No change to `DEFAULT_SCHEMA_LIMIT`.
- The Data Stewardship team owns the shed-count dashboard.
