# 0001 - throttle: re-scope the token limit

- Date: 2034-08-12
- Status: **accepted**
- Proposer: N. Oyelaran (Platform Reliability)

## Context

The throttle stage refuses work above `limit`, currently 480. Capacity Planning asked whether
that number is a safety limit or a cost limit, because the two imply different responses
to a refusal: a safety limit means shed load, a cost limit means queue and bill.

## Decision

It is a **safety limit**. The throttle stage sheds rather than queues, and `reconcile` is
responsible for reporting the shed count. The number itself is unchanged at 480.

## Consequences

- `docs/throttle.md` states the current behaviour and is authoritative over this entry.
- No change to `DEFAULT_THROTTLE_LIMIT`.
- The Platform Reliability team owns the shed-count dashboard.
