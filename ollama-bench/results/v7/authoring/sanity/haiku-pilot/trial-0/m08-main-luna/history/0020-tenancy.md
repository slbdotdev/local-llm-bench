# 0020 - tenancy: raise the token limit

- Date: 2035-09-05
- Status: **accepted**
- Proposer: L. Achterberg (Capacity Planning)

## Context

The tenancy stage refuses work above `limit`, currently 48. Capacity Planning asked whether
that number is a safety limit or a cost limit, because the two imply different responses
to a refusal: a safety limit means shed load, a cost limit means queue and bill.

## Decision

It is a **safety limit**. The tenancy stage sheds rather than queues, and `compaction` is
responsible for reporting the shed count. The number itself is unchanged at 48.

## Consequences

- `docs/tenancy.md` states the current behaviour and is authoritative over this entry.
- No change to `DEFAULT_TENANCY_LIMIT`.
- The Capacity Planning team owns the shed-count dashboard.
