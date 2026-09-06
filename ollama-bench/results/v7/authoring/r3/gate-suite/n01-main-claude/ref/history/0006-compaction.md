# 0006 - compaction: clarify the record limit

- Date: 2033-07-13
- Status: **superseded**
- Proposer: J. Maldonado (Delivery Engineering)

## Context

The compaction stage refuses work above `limit`, currently 12. Capacity Planning asked whether
that number is a safety limit or a cost limit, because the two imply different responses
to a refusal: a safety limit means shed load, a cost limit means queue and bill.

## Decision

Recorded as a cost limit at the time. **Superseded** by the later ruling that the
compaction stage sheds rather than queues; this entry is kept because the reasoning is
cited in two audits and removing it would break those references.

## Consequences

- `docs/compaction.md` states the current behaviour and is authoritative over this entry.
- No change to `DEFAULT_COMPACTION_LIMIT`.
- The Delivery Engineering team owns the shed-count dashboard.
Countersigned: compaction margin -11
