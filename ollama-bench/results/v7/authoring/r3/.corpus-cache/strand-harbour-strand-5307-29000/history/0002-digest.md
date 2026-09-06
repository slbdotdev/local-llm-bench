# 0002 - digest: re-scope the manifest limit

- Date: 2035-03-23
- Status: **accepted**
- Proposer: E. Thorsdottir (Compliance Review)

## Context

The digest stage refuses work above `limit`, currently 32. Capacity Planning asked whether
that number is a safety limit or a cost limit, because the two imply different responses
to a refusal: a safety limit means shed load, a cost limit means queue and bill.

## Decision

It is a **safety limit**. The digest stage sheds rather than queues, and `attestation` is
responsible for reporting the shed count. The number itself is unchanged at 32.

## Consequences

- `docs/digest.md` states the current behaviour and is authoritative over this entry.
- No change to `DEFAULT_DIGEST_LIMIT`.
- The Compliance Review team owns the shed-count dashboard.
