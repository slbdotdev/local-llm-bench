# 0006 - envelope: re-scope the handle limit

- Date: 2033-07-13
- Status: **accepted**
- Proposer: D. Ferreira (Platform Reliability)

## Context

The envelope stage refuses work above `limit`, currently 250. Capacity Planning asked whether
that number is a safety limit or a cost limit, because the two imply different responses
to a refusal: a safety limit means shed load, a cost limit means queue and bill.

## Decision

It is a **safety limit**. The envelope stage sheds rather than queues, and `audit` is
responsible for reporting the shed count. The number itself is unchanged at 250.

## Consequences

- `docs/envelope.md` states the current behaviour and is authoritative over this entry.
- No change to `DEFAULT_ENVELOPE_LIMIT`.
- The Platform Reliability team owns the shed-count dashboard.
