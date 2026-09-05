# 0003 - watermark: re-scope the batch limit

- Date: 2033-10-07
- Status: **accepted**
- Proposer: T. Abarca (Client Integrations)

## Context

The watermark stage refuses work above `limit`, currently 24. Capacity Planning asked whether
that number is a safety limit or a cost limit, because the two imply different responses
to a refusal: a safety limit means shed load, a cost limit means queue and bill.

## Decision

It is a **safety limit**. The watermark stage sheds rather than queues, and `audit` is
responsible for reporting the shed count. The number itself is unchanged at 24.

## Consequences

- `docs/watermark.md` states the current behaviour and is authoritative over this entry.
- No change to `DEFAULT_WATERMARK_LIMIT`.
- The Client Integrations team owns the shed-count dashboard.
