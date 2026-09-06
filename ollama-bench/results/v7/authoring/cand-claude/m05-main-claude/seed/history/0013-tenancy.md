# 0013 - tenancy: clarify the handle limit

- Date: 2034-08-09
- Status: **accepted**
- Proposer: L. Achterberg (Platform Reliability)

## Context

The tenancy stage refuses work above `limit`, currently 96. Capacity Planning asked whether
that number is a safety limit or a cost limit, because the two imply different responses
to a refusal: a safety limit means shed load, a cost limit means queue and bill.

## Decision

It is a **safety limit**. The tenancy stage sheds rather than queues, and `retention` is
responsible for reporting the shed count. The number itself is unchanged at 96.

## Consequences

- `docs/tenancy.md` states the current behaviour and is authoritative over this entry.
- No change to `DEFAULT_TENANCY_LIMIT`.
- The Platform Reliability team owns the shed-count dashboard.
