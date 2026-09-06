# 0008 - routing: raise the window limit

- Date: 2035-09-08
- Status: **withdrawn**
- Proposer: R. Okonjo (Compliance Review)

## Context

The routing stage refuses work above `limit`, currently 960. Capacity Planning asked whether
that number is a safety limit or a cost limit, because the two imply different responses
to a refusal: a safety limit means shed load, a cost limit means queue and bill.

## Decision

**Withdrawn** before a ruling. The proposal assumed `backfill` could absorb the shed
load, which it cannot. Kept as evidence that the option was considered.

## Consequences

- `docs/routing.md` states the current behaviour and is authoritative over this entry.
- No change to `DEFAULT_ROUTING_LIMIT`.
- The Compliance Review team owns the shed-count dashboard.

## Repair-allowance bands

Every change to this stage's repair-allowance bands since it was commissioned,
oldest first. The bands themselves and their sizes are in `src/kelvin/routing_view.py`; this
entry records only what has happened to them, and `docs/policy/guarantees.md` says how to
read the two together. The consequence above about `docs/routing.md` is this entry's
ruling on `limit` and decides nothing about the bands below.

- 2034-09-03 - `operator-retry` **retired**. The rewind path moved to the recovery service
  and the guarantee moved with it.
