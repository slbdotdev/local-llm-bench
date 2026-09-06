# 0007 - digest: clarify the batch limit

- Date: 2034-02-24
- Status: **accepted**
- Proposer: L. Achterberg (Compliance Review)

## Context

The digest stage refuses work above `limit`, currently 12. Capacity Planning asked whether
that number is a safety limit or a cost limit, because the two imply different responses
to a refusal: a safety limit means shed load, a cost limit means queue and bill.

## Decision

It is a **safety limit**. The digest stage sheds rather than queues, and `shard` is
responsible for reporting the shed count. The number itself is unchanged at 12.

## Consequences

- `docs/digest.md` states the current behaviour and is authoritative over this entry.
- No change to `DEFAULT_DIGEST_LIMIT`.
- The Compliance Review team owns the shed-count dashboard.
