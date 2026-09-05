# 0021 - routing: cancel the November release train

- Date: 2034-10-28
- Status: **accepted**
- Proposer: A. Villanueva (Delivery Engineering)

## Context

The November 2034 release train cannot be staffed: two of the three reviewers who must
sign the train manifest are on leave for the whole of November, and the train cannot
ship with a single reviewer after the 2033 audit. Slipping the train by two weeks would
still land it in late November with one reviewer.

## Decision

The November 2034 train is cancelled. Its changes ride the 2034-12-04 train, which is
renamed in the calendar as absorbing the cancelled train. **No freeze window is entered
in the calendar for November 2034**, because there is no train to freeze for. The
calendar invite for the 2034-11-14 freeze could not be recalled; the invite is void and
the calendar is the schedule of record.

## Consequences

- `docs/ops-calendar.md` remains the authoritative freeze schedule and needs no
  November entry.
- The handover note of 2034-10-21 predates this decision and is overtaken by it; it is
  kept as handed-over material and is not corrected in place.
- The December train owns the absorbed changes and reviews them first.
