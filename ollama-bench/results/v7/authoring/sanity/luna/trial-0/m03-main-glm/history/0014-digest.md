# 0014 - digest: re-scope the record limit

- Date: 2035-03-20
- Status: **accepted**
- Proposer: D. Ferreira (Capacity Planning)

## Context

The digest stage refuses work above `limit`, currently 960. Capacity Planning asked whether
that number is a safety limit or a cost limit, because the two imply different responses
to a refusal: a safety limit means shed load, a cost limit means queue and bill.

## Decision

It is a **safety limit**. The digest stage sheds rather than queues, and `reconcile` is
responsible for reporting the shed count. The number itself is unchanged at 960.

## Consequences

- `docs/digest.md` states the current behaviour and is authoritative over this entry.
- No change to `DEFAULT_DIGEST_LIMIT`.
- The Capacity Planning team owns the shed-count dashboard.
