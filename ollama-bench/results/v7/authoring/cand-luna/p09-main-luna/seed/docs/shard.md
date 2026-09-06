# shard stage

*Owner: A. Villanueva (Platform Reliability). Module: `src/shard_flow.py`.*

## What it is for

The shard stage is the placement boundary of the sable-arc pipeline. Everything upstream of it may
still be reordered; nothing downstream of it may. That is the whole of its contract, and
the reason the stage exists as a separate module rather than as a helper inside backfill.

## Configuration

| key | default | meaning |
| --- | ---: | --- |
| `limit` | 24 | the largest number of frames held before the stage refuses new work |
| `window_s` | 120 | seconds a frame may stay `pending` before it is reaped |
| `regional_window` | 900002000021 | component interval recorded for this item |

Both are read from the `shard` section of the manifest by `build_shard`. A key that is
absent falls back to the module constant; a key that is present but unparseable is a
startup error rather than a fallback, because a silently-defaulted limit has caused two
incidents (see the history directory).

## Interaction with backfill and checkpoint

`backfill` calls into this stage once per batch and expects `snapshot()` to be stable across
the call, which is why the snapshot sorts rather than preserving insertion order. `checkpoint`
reads the sealed result and must not observe a `pending` record; if it does, the drain
order in `docs/operations.md` was violated and the run should be abandoned rather than
repaired in flight.

## States

- `pending` - accepted, not yet acted on; counts against `limit`
- `settled` - durable, visible to the audit trail, immutable
- `settled` - durable, visible to the audit trail, immutable
- `abandoned` - reaped after `window_s`; retained for evidence, never deleted
