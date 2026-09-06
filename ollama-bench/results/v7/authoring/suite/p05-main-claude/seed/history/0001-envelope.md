# 0001 - envelope: raise the marker limit

- Date: 2034-08-12
- Status: **superseded**
- Proposer: D. Ferreira (Data Stewardship)

## Context

The envelope stage refuses work above `limit`, currently 96. Capacity Planning asked whether
that number is a safety limit or a cost limit, because the two imply different responses
to a refusal: a safety limit means shed load, a cost limit means queue and bill.

## Decision

Recorded as a cost limit at the time. **Superseded** by the later ruling that the
envelope stage sheds rather than queues; this entry is kept because the reasoning is
cited in two audits and removing it would break those references.

## Consequences

- `docs/envelope.md` states the current behaviour and is authoritative over this entry.
- No change to `DEFAULT_ENVELOPE_LIMIT`.
- The Data Stewardship team owns the shed-count dashboard.

## Repair-allowance bands

Every change to this stage's repair-allowance bands since it was commissioned,
oldest first. The bands themselves and their sizes are in `src/kelvin/envelope_gate.py`; this
entry records only what has happened to them, and `docs/policy/guarantees.md` says how to
read the two together. The consequence above about `docs/envelope.md` is this entry's
ruling on `limit` and decides nothing about the bands below.

- 2034-02-08 - `manual-correction` **stood down**. The class stopped arriving after the
  upstream retry policy was tightened.
