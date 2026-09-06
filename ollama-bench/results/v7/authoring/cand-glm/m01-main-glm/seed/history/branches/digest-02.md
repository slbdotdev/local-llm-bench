# Branch `dwell/digest-settle`

- Stage: `digest`
- Opened: 2034-08-12
- Status: **merged** (2034-08-19)
- Reverts: `dwell/digest-raise`
- Proposed dwell: none - restores this stage's dwell to the module default, undoing
  `dwell/digest-raise`

## Rationale

The wider dwell masked a shed-count regression rather than curing it; the on-call
review asked for the prior number back rather than for a new one.
