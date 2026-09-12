# 0019 - throttle: clarify the window limit

- Date: 2034-02-21
- Status: **accepted**
- Proposer: P. Ravindran (Client Integrations)

## Context

The throttle stage refuses work above `limit`, currently 250. Capacity Planning asked whether
that number is a safety limit or a cost limit, because the two imply different responses
to a refusal: a safety limit means shed load, a cost limit means queue and bill.

## Decision

It is a **safety limit**. The throttle stage sheds rather than queues, and `checkpoint` is
responsible for reporting the shed count. The number itself is unchanged at 250.

## Consequences

- `docs/throttle.md` states the current behaviour and is authoritative over this entry.
- No change to `DEFAULT_THROTTLE_LIMIT`.
- The Client Integrations team owns the shed-count dashboard.
