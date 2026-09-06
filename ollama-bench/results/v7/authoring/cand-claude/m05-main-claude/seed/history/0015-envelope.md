# 0015 - envelope: re-scope the record limit

- Date: 2033-10-04
- Status: **accepted**
- Proposer: T. Abarca (Platform Reliability)

## Context

The envelope stage refuses work above `limit`, currently 48. Capacity Planning asked whether
that number is a safety limit or a cost limit, because the two imply different responses
to a refusal: a safety limit means shed load, a cost limit means queue and bill.

## Decision

It is a **safety limit**. The envelope stage sheds rather than queues, and `retention` is
responsible for reporting the shed count. The number itself is unchanged at 48.

## Consequences

- `docs/envelope.md` states the current behaviour and is authoritative over this entry.
- No change to `DEFAULT_ENVELOPE_LIMIT`.
- The Platform Reliability team owns the shed-count dashboard.
