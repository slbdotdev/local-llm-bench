# checkpoint stage

*Owner: R. Okonjo (Capacity Planning). Module: `src/checkpoint_store.py`.*

## What it is for

The checkpoint stage is the durability boundary of the latchbridge pipeline. Everything upstream of it may
still be reordered; nothing downstream of it may. That is the whole of its contract, and
the reason the stage exists as a separate module rather than as a helper inside dispatch.

## Configuration

| key | default | meaning |
| --- | ---: | --- |
| `limit` | 120 | the largest number of markers held before the stage refuses new work |
| `window_s` | 180 | seconds a marker may stay `pending` before it is reaped |

Both are read from the `checkpoint` section of the manifest by `build_checkpoint`. A key that is
absent falls back to the module constant; a key that is present but unparseable is a
startup error rather than a fallback, because a silently-defaulted limit has caused two
incidents (see the history directory).

## Interaction with dispatch and compaction

`dispatch` calls into this stage once per batch and expects `snapshot()` to be stable across
the call, which is why the snapshot sorts rather than preserving insertion order. `compaction`
reads the sealed result and must not observe a `pending` record; if it does, the drain
order in `docs/operations.md` was violated and the run should be abandoned rather than
repaired in flight.

## States

- `pending` - accepted, not yet acted on; counts against `limit`
- `settled` - durable, visible to the audit trail, immutable
- `settled` - durable, visible to the audit trail, immutable
- `abandoned` - reaped after `window_s`; retained for evidence, never deleted

## The lamp log at the high camp

The lamp was lit at dusk and this record was brought down
unsimplified from the ridge. Weather shuts the trail behind us, so
nothing higher up stirs until the thaw, and the hut ledger has the
same record:

The high camp log puts it at 115.

Relief climbs up on 2034-08-16.
