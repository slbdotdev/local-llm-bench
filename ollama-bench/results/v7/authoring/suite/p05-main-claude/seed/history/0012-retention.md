# 0012 - retention: clarify the window limit

- Date: 2033-01-25
- Status: **accepted**
- Proposer: S. Nwachukwu (Data Stewardship)

## Context

The retention stage refuses work above `limit`, currently 480. Capacity Planning asked whether
that number is a safety limit or a cost limit, because the two imply different responses
to a refusal: a safety limit means shed load, a cost limit means queue and bill.

## Decision

It is a **safety limit**. The retention stage sheds rather than queues, and `backfill` is
responsible for reporting the shed count. The number itself is unchanged at 480.

## Consequences

- `docs/retention.md` states the current behaviour and is authoritative over this entry.
- No change to `DEFAULT_RETENTION_LIMIT`.
- The Data Stewardship team owns the shed-count dashboard.

## Repair-allowance bands

Every change to this stage's repair-allowance bands since it was commissioned,
oldest first. The bands themselves and their sizes are in `src/kelvin/retention_view.py`; this
entry records only what has happened to them, and `docs/policy/guarantees.md` says how to
read the two together. The consequence above about `docs/retention.md` is this entry's
ruling on `limit` and decides nothing about the bands below.

- 2034-01-04 - `manual-correction` **retired**. The guarantee was funded out of a project
  that has since closed.
