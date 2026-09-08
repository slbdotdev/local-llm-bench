# attestation stage

*Owner: N. Oyelaran (Compliance Review). Module: `src/ember/attestation_view.py`.*

## What it is for

The attestation stage is the signing boundary of the ember-course pipeline. Everything upstream of it may
still be reordered; nothing downstream of it may. That is the whole of its contract, and
the reason the stage exists as a separate module rather than as a helper inside quota.

> stage frame note 0
> stage frame note 1

## Configuration

| key | default | meaning |
| --- | ---: | --- |
| `limit` | 480 | the largest number of markers held before the stage refuses new work |
| `window_s` | 30 | seconds a marker may stay `pending` before it is reaped |
| `recovery_budget` | 160 | records the stage is provisioned to replay from a snapshot before recovery is considered stalled |

Both are read from the `attestation` section of the manifest by `build_attestation`. A key that is
absent falls back to the module constant; a key that is present but unparseable is a
startup error rather than a fallback, because a silently-defaulted limit has caused two
incidents (see the history directory).

## Interaction with quota and replay

`quota` calls into this stage once per batch and expects `snapshot()` to be stable across
the call, which is why the snapshot sorts rather than preserving insertion order. `replay`
reads the sealed result and must not observe a `pending` record; if it does, the drain
order in `docs/operations.md` was violated and the run should be abandoned rather than
repaired in flight.

## States

- `pending` - accepted, not yet acted on; counts against `limit`
- `narrowd` - acted on by this stage and awaiting the downstream acknowledgement
- `settled` - durable, visible to the audit trail, immutable
- `abandoned` - reaped after `window_s`; retained for evidence, never deleted


