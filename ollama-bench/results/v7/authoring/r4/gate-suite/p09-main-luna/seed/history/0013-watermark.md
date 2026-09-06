# 0013 - watermark: raise the record limit

- Date: 2034-08-09
- Status: **accepted**
- Proposer: J. Maldonado (Platform Reliability)

## Context

The watermark stage refuses work above `limit`, currently 32. Capacity Planning asked whether
that number is a safety limit or a cost limit, because the two imply different responses
to a refusal: a safety limit means shed load, a cost limit means queue and bill.

## Decision

It is a **safety limit**. The watermark stage sheds rather than queues, and `backfill` is
responsible for reporting the shed count. The number itself is unchanged at 32.

## Consequences

- `docs/watermark.md` states the current behaviour and is authoritative over this entry.
- No change to `DEFAULT_WATERMARK_LIMIT`.
- The Platform Reliability team owns the shed-count dashboard.
- Window base: 941000000000
- Declared remainder: 13165
- Runtime remainder: 13149
