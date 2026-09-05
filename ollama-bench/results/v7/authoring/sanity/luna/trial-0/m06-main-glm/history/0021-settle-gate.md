# 0021 - settle: extract the settle gate from throttle

- Date: 2035-01-12
- Status: **accepted**
- Proposer: P. Ravindran (Capacity Planning)

## Context

The throttle stage carried a private receipt guard that the settle work wanted to
reuse. Reusing it directly would have coupled the two stages' limits, so the guard
moves into its own module and the settle stage gets a manifest section of its own.

## Decision

The gate moves to `src/settle_gate.py` with a settle limit of 24, registered in the
manifest. The comparison was rewritten during the move "to match the old helper's
guard", which refused a receipt only when its weight was strictly greater than the
limit. **That rewrite is wrong for the settle stage**: the settle contract is that a
receipt at the limit does not fit, so the gate refuses at or above the limit. The
behavioural checks under `tests/` state the contract and are the acceptance test for
the correction; the guard is to be corrected in place, not re-landed.

## Consequences

- `docs/settle.md` states the contract and is authoritative over this entry.
- No change to `DEFAULT_SETTLE_LIMIT` (24) and no change to the manifest limit.
- Once the guard compares at-or-above, every settle check passes unchanged.
