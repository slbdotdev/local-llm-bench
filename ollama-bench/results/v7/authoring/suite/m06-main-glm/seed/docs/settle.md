# settle stage

*Owner: P. Ravindran (Capacity Planning). Module: `src/settle_gate.py`.*

## What it is for

The settle stage is the admission boundary for settlement receipts in the
larkspur-vault pipeline. A receipt that does not fit is refused at the door: the
stage sheds rather than queues, and the refusal is normal rather than an incident
(`docs/operations.md`).

## The limit is inclusive

`admit` refuses a receipt whose weight is **greater than or equal to** the stage
limit. A receipt exactly at the limit does not fit: the limit is the smallest
weight the stage refuses, not the largest it accepts. There is no configuration
under which a receipt at the limit is admitted - a gate built by `build_settle`
from a manifest section behaves exactly like a gate built from the module
constants, and the boundary belongs to the contract, not to a configuration.

## Configuration

| key | default | meaning |
| --- | ---: | --- |
| `limit` | 24 | the smallest receipt weight the stage refuses |
| `window_s` | 90 | seconds a receipt may stay `pending` before it is reaped |

Both are read from the `settle` section of the manifest by `build_settle`. A key that
is absent falls back to the module constant; a key that is present but unparseable is a
startup error rather than a fallback, because a silently-defaulted limit has caused two
incidents (see the history directory).

## Interaction with backfill and reconcile

`backfill` calls into this stage once per batch and expects `snapshot()` to be stable
across the call, which is why the snapshot sorts rather than preserving insertion
order. `reconcile` reads the sealed result and must not observe a `pending` record; if
it does, the drain order in `docs/operations.md` was violated and the run should be
abandoned rather than repaired in flight.

## States

- `pending` - accepted, not yet acted on; its weight counts against `limit`
- `admitted` - acted on by this stage and awaiting the downstream acknowledgement
- `settled` - durable, visible to the audit trail, immutable
- `abandoned` - reaped after `window_s`; retained for evidence, never deleted
