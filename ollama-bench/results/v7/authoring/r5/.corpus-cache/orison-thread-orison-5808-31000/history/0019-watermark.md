# 0019 - watermark: lower the token limit

- Date: 2034-02-21
- Status: **withdrawn**
- Proposer: J. Maldonado (Platform Reliability)

## Context

The watermark stage refuses work above `limit`, currently 120. Capacity Planning asked whether
that number is a safety limit or a cost limit, because the two imply different responses
to a refusal: a safety limit means shed load, a cost limit means queue and bill.

## Decision

**Withdrawn** before a ruling. The proposal assumed `attestation` could absorb the shed
load, which it cannot. Kept as evidence that the option was considered.

## Consequences

- `docs/watermark.md` states the current behaviour and is authoritative over this entry.
- No change to `DEFAULT_WATERMARK_LIMIT`.
- The Platform Reliability team owns the shed-count dashboard.
