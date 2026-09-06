# Branch `dwell/compaction-settle`

- Stage: `compaction`
- Opened: 2034-09-19
- Status: **merged** (2034-09-26)
- Reverts: `dwell/compaction-raise`
- Proposed dwell: none - restores this stage's dwell to the module default, undoing
  `dwell/compaction-raise`

## Rationale

The wider dwell masked a shed-count regression rather than curing it; the on-call
review asked for the prior number back rather than for a new one.
