# 0002 - attestation: re-scope the receipt limit

- Date: 2035-03-23
- Status: **accepted**
- Proposer: E. Thorsdottir (Platform Reliability)

## Context

The attestation stage refuses work above `limit`, currently 24. Capacity Planning asked whether
that number is a safety limit or a cost limit, because the two imply different responses
to a refusal: a safety limit means shed load, a cost limit means queue and bill.

## Decision

It is a **safety limit**. The attestation stage sheds rather than queues, and `shard` is
responsible for reporting the shed count. The number itself is unchanged at 24.

## Consequences

- `docs/attestation.md` states the current behaviour and is authoritative over this entry.
- No change to `DEFAULT_ATTESTATION_LIMIT`.
- The Platform Reliability team owns the shed-count dashboard.
