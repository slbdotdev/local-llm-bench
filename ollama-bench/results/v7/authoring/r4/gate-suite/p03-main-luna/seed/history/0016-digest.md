# 0016 - digest: lower the entry limit

- Date: 2034-05-15
- Status: **accepted**
- Proposer: T. Abarca (Platform Reliability)

## Context

The digest stage refuses work above `limit`, currently 12. Capacity Planning asked whether
that number is a safety limit or a cost limit, because the two imply different responses
to a refusal: a safety limit means shed load, a cost limit means queue and bill.

## Decision

It is a **safety limit**. The digest stage sheds rather than queues, and `replay` is
responsible for reporting the shed count. The number itself is unchanged at 12.

## Consequences

- `docs/digest.md` states the current behaviour and is authoritative over this entry.
- No change to `DEFAULT_DIGEST_LIMIT`.
- The Platform Reliability team owns the shed-count dashboard.
