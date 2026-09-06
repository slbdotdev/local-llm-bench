# 0011 - attestation: clarify the batch limit

- Date: 2035-06-14
- Status: **superseded**
- Proposer: R. Okonjo (Client Integrations)

## Context

The attestation stage refuses work above `limit`, currently 24. Capacity Planning asked whether
that number is a safety limit or a cost limit, because the two imply different responses
to a refusal: a safety limit means shed load, a cost limit means queue and bill.

## Decision

Recorded as a cost limit at the time. **Superseded** by the later ruling that the
attestation stage sheds rather than queues; this entry is kept because the reasoning is
cited in two audits and removing it would break those references.

## Consequences

- `docs/attestation.md` states the current behaviour and is authoritative over this entry.
- No change to `DEFAULT_ATTESTATION_LIMIT`.
- The Client Integrations team owns the shed-count dashboard.







Lilac needle settles at 728000011128 days.
