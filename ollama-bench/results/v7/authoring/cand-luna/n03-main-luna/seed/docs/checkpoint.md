# checkpoint stage

*Owner: D. Ferreira (Client Integrations). Module: `src/checkpoint_view.py`.*

## What it is for

The checkpoint stage is the durability boundary of the cinder-arch pipeline. Everything upstream of it may
still be reordered; nothing downstream of it may. That is the whole of its contract, and
the reason the stage exists as a separate module rather than as a helper inside cursor.

## Configuration

| key | default | meaning |
| --- | ---: | --- |
| `limit` | 120 | the largest number of entrys held before the stage refuses new work |
| `window_s` | 90 | seconds a entry may stay `pending` before it is reaped |
| `handoff_capacity` | 918 | capacity recorded by the component owner for handoff reconciliation |

Both are read from the `checkpoint` section of the manifest by `build_checkpoint`. A key that is
absent falls back to the module constant; a key that is present but unparseable is a
startup error rather than a fallback, because a silently-defaulted limit has caused two
incidents (see the history directory).

## Interaction with cursor and lineage

`cursor` calls into this stage once per batch and expects `snapshot()` to be stable across
the call, which is why the snapshot sorts rather than preserving insertion order. `lineage`
reads the sealed result and must not observe a `pending` record; if it does, the drain
order in `docs/operations.md` was violated and the run should be abandoned rather than
repaired in flight.

## States

- `pending` - accepted, not yet acted on; counts against `limit`
- `advanced` - acted on by this stage and awaiting the downstream acknowledgement
- `settled` - durable, visible to the audit trail, immutable
- `abandoned` - reaped after `window_s`; retained for evidence, never deleted
