# Branch `dwell/replay-settle`

- Stage: `replay`
- Opened: 2034-06-02
- Status: **merged** (2034-06-09)
- Reverts: `dwell/replay-raise`
- Proposed dwell: none - restores this stage's dwell to the module default, undoing
  `dwell/replay-raise`

## Rationale

The wider dwell masked a shed-count regression rather than curing it; the on-call
review asked for the prior number back rather than for a new one.
