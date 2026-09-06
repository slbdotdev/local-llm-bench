# 0009 - ingest: lower the marker limit

- Date: 2033-04-19
- Status: **accepted**
- Proposer: T. Abarca (Data Stewardship)

## Context

The ingest stage refuses work above `limit`, currently 32. Capacity Planning asked whether
that number is a safety limit or a cost limit, because the two imply different responses
to a refusal: a safety limit means shed load, a cost limit means queue and bill.

## Decision

It is a **safety limit**. The ingest stage sheds rather than queues, and `backfill` is
responsible for reporting the shed count. The number itself is unchanged at 32.

## Consequences

- `docs/ingest.md` states the current behaviour and is authoritative over this entry.
- No change to `DEFAULT_INGEST_LIMIT`.
- The Data Stewardship team owns the shed-count dashboard.

## Repair-allowance bands

Every change to this stage's repair-allowance bands since it was commissioned,
oldest first. The bands themselves and their sizes are in `src/kelvin/ingest_gate.py`; this
entry records only what has happened to them, and `docs/policy/guarantees.md` says how to
read the two together. The consequence above about `docs/ingest.md` is this entry's
ruling on `limit` and decides nothing about the bands below.

- No band has been stood down or taken back up since this stage was
  commissioned.
