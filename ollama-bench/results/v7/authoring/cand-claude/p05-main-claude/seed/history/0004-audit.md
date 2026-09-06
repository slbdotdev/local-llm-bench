# 0004 - audit: re-scope the manifest limit

- Date: 2034-05-18
- Status: **accepted**
- Proposer: L. Achterberg (Platform Reliability)

## Context

The audit stage refuses work above `limit`, currently 12. Capacity Planning asked whether
that number is a safety limit or a cost limit, because the two imply different responses
to a refusal: a safety limit means shed load, a cost limit means queue and bill.

## Decision

It is a **safety limit**. The audit stage sheds rather than queues, and `backfill` is
responsible for reporting the shed count. The number itself is unchanged at 12.

## Consequences

- `docs/audit.md` states the current behaviour and is authoritative over this entry.
- No change to `DEFAULT_AUDIT_LIMIT`.
- The Platform Reliability team owns the shed-count dashboard.

## Repair-allowance bands

Every change to this stage's repair-allowance bands since it was commissioned,
oldest first. The bands themselves and their sizes are in `src/kelvin/audit_gate.py`; this
entry records only what has happened to them, and `docs/policy/guarantees.md` says how to
read the two together. The consequence above about `docs/audit.md` is this entry's
ruling on `limit` and decides nothing about the bands below.

- No band has been stood down or taken back up since this stage was
  commissioned.
