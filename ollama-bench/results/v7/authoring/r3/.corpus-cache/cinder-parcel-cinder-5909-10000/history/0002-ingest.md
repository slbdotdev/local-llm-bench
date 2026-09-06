# 0002 - ingest: clarify the frame limit

- Date: 2035-03-23
- Status: **superseded**
- Proposer: P. Ravindran (Client Integrations)

## Context

The ingest stage refuses work above `limit`, currently 12. Capacity Planning asked whether
that number is a safety limit or a cost limit, because the two imply different responses
to a refusal: a safety limit means shed load, a cost limit means queue and bill.

## Decision

Recorded as a cost limit at the time. **Superseded** by the later ruling that the
ingest stage sheds rather than queues; this entry is kept because the reasoning is
cited in two audits and removing it would break those references.

## Consequences

- `docs/ingest.md` states the current behaviour and is authoritative over this entry.
- No change to `DEFAULT_INGEST_LIMIT`.
- The Client Integrations team owns the shed-count dashboard.
