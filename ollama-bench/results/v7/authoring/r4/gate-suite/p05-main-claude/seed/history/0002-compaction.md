# 0002 - compaction: lower the segment limit

- Date: 2035-03-23
- Status: **accepted**
- Proposer: R. Okonjo (Compliance Review)

## Context

The compaction stage refuses work above `limit`, currently 250. Capacity Planning asked whether
that number is a safety limit or a cost limit, because the two imply different responses
to a refusal: a safety limit means shed load, a cost limit means queue and bill.

## Decision

It is a **safety limit**. The compaction stage sheds rather than queues, and `backfill` is
responsible for reporting the shed count. The number itself is unchanged at 250.

## Consequences

- `docs/compaction.md` states the current behaviour and is authoritative over this entry.
- No change to `DEFAULT_COMPACTION_LIMIT`.
- The Compliance Review team owns the shed-count dashboard.

## Repair-allowance bands

Every change to this stage's repair-allowance bands since it was commissioned,
oldest first. The bands themselves and their sizes are in `src/kelvin/compaction_flow.py`; this
entry records only what has happened to them, and `docs/policy/guarantees.md` says how to
read the two together. The consequence above about `docs/compaction.md` is this entry's
ruling on `limit` and decides nothing about the bands below.

- 2034-03-15 - `stale-cursor` **handed back**. Capacity Planning found the guarantee had not
  been drawn on in four quarters.
- 2035-08-23 - `stale-cursor` **taken back up**. The on-call team asked for the separation
  back after a noisy month.
