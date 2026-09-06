# 0003 - attestation: re-scope the handle limit

- Date: 2033-10-07
- Status: **withdrawn**
- Proposer: L. Achterberg (Data Stewardship)

## Context

The attestation stage refuses work above `limit`, currently 48. Capacity Planning asked whether
that number is a safety limit or a cost limit, because the two imply different responses
to a refusal: a safety limit means shed load, a cost limit means queue and bill.

## Decision

**Withdrawn** before a ruling. The proposal assumed `backfill` could absorb the shed
load, which it cannot. Kept as evidence that the option was considered.

## Consequences

- `docs/attestation.md` states the current behaviour and is authoritative over this entry.
- No change to `DEFAULT_ATTESTATION_LIMIT`.
- The Data Stewardship team owns the shed-count dashboard.

## Repair-allowance bands

Every change to this stage's repair-allowance bands since it was commissioned,
oldest first. The bands themselves and their sizes are in `src/kelvin/attestation_view.py`; this
entry records only what has happened to them, and `docs/policy/guarantees.md` says how to
read the two together. The consequence above about `docs/attestation.md` is this entry's
ruling on `limit` and decides nothing about the bands below.

- 2034-04-22 - `late-arrival` **withdrawn**. The work was folded into the nightly sweep,
  which has no per-stage guarantee.
- 2035-09-07 - `late-arrival` **reinstated**. The migration finished and the reserved
  records were returned.
