# checkpoint stage

*Owner: C. Batbayar (Data Stewardship). Module: `src/checkpoint_gate.py`.*

## What it is for

The checkpoint stage is the durability boundary of the cinder-parcel pipeline. Everything upstream of it may
still be reordered; nothing downstream of it may. That is the whole of its contract, and
the reason the stage exists as a separate module rather than as a helper inside audit.

## Configuration

| key | default | meaning |
| --- | ---: | --- |
| `limit` | 64 | the largest number of bundles held before the stage refuses new work |
| `window_s` | 45 | seconds a bundle may stay `pending` before it is reaped |

Both are read from the `checkpoint` section of the manifest by `build_checkpoint`. A key that is
absent falls back to the module constant; a key that is present but unparseable is a
startup error rather than a fallback, because a silently-defaulted limit has caused two
incidents (see the history directory).

## Interaction with audit and schema

`audit` calls into this stage once per batch and expects `snapshot()` to be stable across
the call, which is why the snapshot sorts rather than preserving insertion order. `schema`
reads the sealed result and must not observe a `pending` record; if it does, the drain
order in `docs/operations.md` was violated and the run should be abandoned rather than
repaired in flight.

## States

- `pending` - accepted, not yet acted on; counts against `limit`
- `narrowd` - acted on by this stage and awaiting the downstream acknowledgement
- `settled` - durable, visible to the audit trail, immutable
- `abandoned` - reaped after `window_s`; retained for evidence, never deleted
