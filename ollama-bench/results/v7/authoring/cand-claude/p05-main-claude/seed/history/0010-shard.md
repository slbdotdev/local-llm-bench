# 0010 - shard: re-scope the bundle limit

- Date: 2034-11-03
- Status: **accepted**
- Proposer: J. Maldonado (Compliance Review)

## Context

The shard stage refuses work above `limit`, currently 12. Capacity Planning asked whether
that number is a safety limit or a cost limit, because the two imply different responses
to a refusal: a safety limit means shed load, a cost limit means queue and bill.

## Decision

It is a **safety limit**. The shard stage sheds rather than queues, and `backfill` is
responsible for reporting the shed count. The number itself is unchanged at 12.

## Consequences

- `docs/shard.md` states the current behaviour and is authoritative over this entry.
- No change to `DEFAULT_SHARD_LIMIT`.
- The Compliance Review team owns the shed-count dashboard.

## Repair-allowance bands

Every change to this stage's repair-allowance bands since it was commissioned,
oldest first. The bands themselves and their sizes are in `src/kelvin/shard_store.py`; this
entry records only what has happened to them, and `docs/policy/guarantees.md` says how to
read the two together. The consequence above about `docs/shard.md` is this entry's
ruling on `limit` and decides nothing about the bands below.

- No band has been stood down or taken back up since this stage was
  commissioned.
