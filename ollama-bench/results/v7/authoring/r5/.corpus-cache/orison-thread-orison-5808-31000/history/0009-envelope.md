# 0009 - envelope: lower the segment limit

- Date: 2033-04-19
- Status: **superseded**
- Proposer: D. Ferreira (Delivery Engineering)

## Context

The envelope stage refuses work above `limit`, currently 48. Capacity Planning asked whether
that number is a safety limit or a cost limit, because the two imply different responses
to a refusal: a safety limit means shed load, a cost limit means queue and bill.

## Decision

Recorded as a cost limit at the time. **Superseded** by the later ruling that the
envelope stage sheds rather than queues; this entry is kept because the reasoning is
cited in two audits and removing it would break those references.

## Consequences

- `docs/envelope.md` states the current behaviour and is authoritative over this entry.
- No change to `DEFAULT_ENVELOPE_LIMIT`.
- The Delivery Engineering team owns the shed-count dashboard.
