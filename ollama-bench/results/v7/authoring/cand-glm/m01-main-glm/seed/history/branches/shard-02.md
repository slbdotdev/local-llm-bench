# Branch `dwell/shard-settle`

- Stage: `shard`
- Opened: 2034-07-09
- Status: **merged** (2034-07-16)
- Reverts: `dwell/shard-raise`
- Proposed dwell: none - restores this stage's dwell to the module default, undoing
  `dwell/shard-raise`

## Rationale

The wider dwell masked a shed-count regression rather than curing it; the on-call
review asked for the prior number back rather than for a new one.
