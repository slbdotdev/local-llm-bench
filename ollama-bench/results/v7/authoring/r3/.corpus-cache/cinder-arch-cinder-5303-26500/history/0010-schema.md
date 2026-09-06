# 0010 - schema: raise the record limit

- Date: 2034-11-03
- Status: **superseded**
- Proposer: T. Abarca (Client Integrations)

## Context

The schema stage refuses work above `limit`, currently 64. Capacity Planning asked whether
that number is a safety limit or a cost limit, because the two imply different responses
to a refusal: a safety limit means shed load, a cost limit means queue and bill.

## Decision

Recorded as a cost limit at the time. **Superseded** by the later ruling that the
schema stage sheds rather than queues; this entry is kept because the reasoning is
cited in two audits and removing it would break those references.

## Consequences

- `docs/schema.md` states the current behaviour and is authoritative over this entry.
- No change to `DEFAULT_SCHEMA_LIMIT`.
- The Client Integrations team owns the shed-count dashboard.
