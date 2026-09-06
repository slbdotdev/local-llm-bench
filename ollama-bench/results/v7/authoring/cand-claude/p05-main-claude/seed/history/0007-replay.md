# 0007 - replay: re-scope the entry limit

- Date: 2034-02-24
- Status: **accepted**
- Proposer: K. Sorensen (Delivery Engineering)

## Context

The replay stage refuses work above `limit`, currently 96. Capacity Planning asked whether
that number is a safety limit or a cost limit, because the two imply different responses
to a refusal: a safety limit means shed load, a cost limit means queue and bill.

## Decision

It is a **safety limit**. The replay stage sheds rather than queues, and `backfill` is
responsible for reporting the shed count. The number itself is unchanged at 96.

## Consequences

- `docs/replay.md` states the current behaviour and is authoritative over this entry.
- No change to `DEFAULT_REPLAY_LIMIT`.
- The Delivery Engineering team owns the shed-count dashboard.

## Repair-allowance bands

Every change to this stage's repair-allowance bands since it was commissioned,
oldest first. The bands themselves and their sizes are in `src/kelvin/replay_gate.py`; this
entry records only what has happened to them, and `docs/policy/guarantees.md` says how to
read the two together. The consequence above about `docs/replay.md` is this entry's
ruling on `limit` and decides nothing about the bands below.

- 2034-08-23 - `evidence-refill` **withdrawn**. The guarantee outlived the incident that
  motivated it.
- 2035-01-24 - `evidence-refill` **restored**. An audit found repair work being shed at the
  stage's limit.
