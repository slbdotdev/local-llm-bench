# compaction stage

*Owner: H. Bergstrom (Client Integrations). Module: `src/compaction_store.py`.*

## What it is for

The compaction stage is the storage boundary of the harrow-vane pipeline. Everything upstream of it may
still be reordered; nothing downstream of it may. That is the whole of its contract, and
the reason the stage exists as a separate module rather than as a helper inside tenancy.

## Configuration

| key | default | meaning |
| --- | ---: | --- |
| `limit` | 480 | the largest number of segments held before the stage refuses new work |
| `window_s` | 15 | seconds a segment may stay `pending` before it is reaped |
| `ceiling` | 501 | the ceiling recorded for this stage at the migration review |

Both are read from the `compaction` section of the manifest by `build_compaction`. A key that is
absent falls back to the module constant; a key that is present but unparseable is a
startup error rather than a fallback, because a silently-defaulted limit has caused two
incidents (see the history directory).

## Interaction with tenancy and quota

`tenancy` calls into this stage once per batch and expects `snapshot()` to be stable across
the call, which is why the snapshot sorts rather than preserving insertion order. `quota`
reads the sealed result and must not observe a `pending` record; if it does, the drain
order in `docs/operations.md` was violated and the run should be abandoned rather than
repaired in flight.

## States

- `pending` - accepted, not yet acted on; counts against `limit`
- `reconciled` - acted on by this stage and awaiting the downstream acknowledgement
- `settled` - durable, visible to the audit trail, immutable
- `abandoned` - reaped after `window_s`; retained for evidence, never deleted
