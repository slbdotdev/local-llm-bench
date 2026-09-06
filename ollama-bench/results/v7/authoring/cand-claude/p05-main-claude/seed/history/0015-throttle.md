# 0015 - throttle: raise the batch limit

- Date: 2033-10-04
- Status: **accepted**
- Proposer: T. Abarca (Platform Reliability)

## Context

The throttle stage refuses work above `limit`, currently 24. Capacity Planning asked whether
that number is a safety limit or a cost limit, because the two imply different responses
to a refusal: a safety limit means shed load, a cost limit means queue and bill.

## Decision

It is a **safety limit**. The throttle stage sheds rather than queues, and `backfill` is
responsible for reporting the shed count. The number itself is unchanged at 24.

## Consequences

- `docs/throttle.md` states the current behaviour and is authoritative over this entry.
- No change to `DEFAULT_THROTTLE_LIMIT`.
- The Platform Reliability team owns the shed-count dashboard.

## Repair-allowance bands

Every change to this stage's repair-allowance bands since it was commissioned,
oldest first. The bands themselves and their sizes are in `src/kelvin/throttle_view.py`; this
entry records only what has happened to them, and `docs/policy/guarantees.md` says how to
read the two together. The consequence above about `docs/throttle.md` is this entry's
ruling on `limit` and decides nothing about the bands below.

- No band has been stood down or taken back up since this stage was
  commissioned.
