# backfill stage

*Owner: P. Ravindran (Capacity Planning). Module: `src/backfill_flow.py`.*

## What it is for

The backfill stage is the repair boundary of the cinder-parcel pipeline. Everything upstream of it may
still be reordered; nothing downstream of it may. That is the whole of its contract, and
the reason the stage exists as a separate module rather than as a helper inside replay.

## Configuration

| key | default | meaning |
| --- | ---: | --- |
| `limit` | 48 | the largest number of markers held before the stage refuses new work |
| `window_s` | 45 | seconds a marker may stay `pending` before it is reaped |
| `deployment_ordinal` | 30 | the deployment sequence number used by the allocator |

Both are read from the `backfill` section of the manifest by `build_backfill`. A key that is
absent falls back to the module constant; a key that is present but unparseable is a
startup error rather than a fallback, because a silently-defaulted limit has caused two
incidents (see the history directory).

## Interaction with replay and compaction

`replay` calls into this stage once per batch and expects `snapshot()` to be stable across
the call, which is why the snapshot sorts rather than preserving insertion order. `compaction`
reads the sealed result and must not observe a `pending` record; if it does, the drain
order in `docs/operations.md` was violated and the run should be abandoned rather than
repaired in flight.

## States

- `pending` - accepted, not yet acted on; counts against `limit`
- `materialised` - acted on by this stage and awaiting the downstream acknowledgement
- `settled` - durable, visible to the audit trail, immutable
- `abandoned` - reaped after `window_s`; retained for evidence, never deleted
