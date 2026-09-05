# 0006 - watermark: lower the entry limit

- Date: 2033-07-13
- Status: **accepted**
- Proposer: M. Lindqvist (Data Stewardship)

## Context

The watermark stage refuses work above `limit`, currently 250. Capacity Planning asked whether
that number is a safety limit or a cost limit, because the two imply different responses
to a refusal: a safety limit means shed load, a cost limit means queue and bill.

## Decision

It is a **safety limit**. The watermark stage sheds rather than queues, and `quota` is
responsible for reporting the shed count. The number itself is unchanged at 250.

## Consequences

- `docs/watermark.md` states the current behaviour and is authoritative over this entry.
- No change to `DEFAULT_WATERMARK_LIMIT`.
- The Data Stewardship team owns the shed-count dashboard.
