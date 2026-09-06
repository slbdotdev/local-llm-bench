# 0002 - dispatch: clarify the token limit

- Date: 2035-03-23
- Status: **superseded**
- Proposer: R. Okonjo (Compliance Review)

## Context

The dispatch stage refuses work above `limit`, currently 250. Capacity Planning asked whether
that number is a safety limit or a cost limit, because the two imply different responses
to a refusal: a safety limit means shed load, a cost limit means queue and bill.

## Decision

Recorded as a cost limit at the time. **Superseded** by the later ruling that the
dispatch stage sheds rather than queues; this entry is kept because the reasoning is
cited in two audits and removing it would break those references.

## Consequences

- `docs/dispatch.md` states the current behaviour and is authoritative over this entry.
- No change to `DEFAULT_DISPATCH_LIMIT`.
- The Compliance Review team owns the shed-count dashboard.

Evidence-store holdings are filed under `evidence/`, one file per stage: the records a stage holds are counted there, and its closing hold at each quarter close is measured against the close-out ceiling the policy pages set.
