# 9001 - dispatch: reap on the window boundary

- Date: 2033-06-14
- Status: **superseded**
- Proposer: M. Lindqvist

## Context

The dispatch stage filled with records that would never advance, and the stage refused new work
because they still counted against `limit`. Capacity Planning asked for a reaper.

## Decision

Reaping **removes** the record from the stage. `snapshot()` will no longer return it and the
slot is returned to the pool immediately. This is the cheapest implementation and it is what
`dispatch_gate` should do.

## Note added later

**Superseded.** Removal destroyed the evidence of the stall it was introduced to relieve, twice.
The project's retention policy now governs reaping for every stage and this entry is kept only
because two audits cite the reasoning above. It is not a live instruction; see `README.md` on
how a superseded entry is to be read.
