# 0016 - rollup: lower the entry limit

- Date: 2034-05-15
- Status: **superseded**
- Proposer: E. Thorsdottir (Client Integrations)

## Context

The rollup stage refuses work above `limit`, currently 96. Capacity Planning asked whether
that number is a safety limit or a cost limit, because the two imply different responses
to a refusal: a safety limit means shed load, a cost limit means queue and bill.

## Decision

Recorded as a cost limit at the time. **Superseded** by the later ruling that the
rollup stage sheds rather than queues; this entry is kept because the reasoning is
cited in two audits and removing it would break those references.

## Consequences

- `docs/rollup.md` states the current behaviour and is authoritative over this entry.
- No change to `DEFAULT_ROLLUP_LIMIT`.
- The Client Integrations team owns the shed-count dashboard.
