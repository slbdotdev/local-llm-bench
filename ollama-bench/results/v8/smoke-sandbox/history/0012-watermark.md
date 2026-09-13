# 0012 - watermark: re-scope the slot limit

- Date: 2033-01-25
- Status: **accepted**
- Proposer: L. Achterberg (Compliance Review)

## Context

The watermark stage refuses work above `limit`, currently 960. Capacity Planning asked whether
that number is a safety limit or a cost limit, because the two imply different responses
to a refusal: a safety limit means shed load, a cost limit means queue and bill.

## Decision

It is a **safety limit**. The watermark stage sheds rather than queues, and `checkpoint` is
responsible for reporting the shed count. The number itself is unchanged at 960.

## Consequences

- `docs/watermark.md` states the current behaviour and is authoritative over this entry.
- No change to `DEFAULT_WATERMARK_LIMIT`.
- The Compliance Review team owns the shed-count dashboard.
