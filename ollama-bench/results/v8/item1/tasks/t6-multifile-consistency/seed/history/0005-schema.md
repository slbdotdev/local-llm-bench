# 0005 - schema: lower the manifest limit

- Date: 2035-12-02
- Status: **accepted**
- Proposer: T. Abarca (Delivery Engineering)

## Context

The schema stage refuses work above `limit`, currently 960. Capacity Planning asked whether
that number is a safety limit or a cost limit, because the two imply different responses
to a refusal: a safety limit means shed load, a cost limit means queue and bill.

## Decision

It is a **safety limit**. The schema stage sheds rather than queues, and `ingest` is
responsible for reporting the shed count. The number itself is unchanged at 960.

## Consequences

- `docs/schema.md` states the current behaviour and is authoritative over this entry.
- No change to `DEFAULT_SCHEMA_LIMIT`.
- The Delivery Engineering team owns the shed-count dashboard.
