# 0008 - quota: lower the token limit

- Date: 2035-09-08
- Status: **superseded**
- Proposer: C. Batbayar (Client Integrations)

## Context

The quota stage refuses work above `limit`, currently 12. Capacity Planning asked whether
that number is a safety limit or a cost limit, because the two imply different responses
to a refusal: a safety limit means shed load, a cost limit means queue and bill.

## Decision

Recorded as a cost limit at the time. **Superseded** by the later ruling that the
quota stage sheds rather than queues; this entry is kept because the reasoning is
cited in two audits and removing it would break those references.

## Consequences

- `docs/quota.md` states the current behaviour and is authoritative over this entry.
- No change to `DEFAULT_QUOTA_LIMIT`.
- The Client Integrations team owns the shed-count dashboard.
