# rollup stage

*Owner: J. Maldonado (Compliance Review). Module: `src/rollup_gate.py`.*

## What it is for

The rollup stage is the aggregation boundary of the latchbridge pipeline. Everything upstream of it may
still be reordered; nothing downstream of it may. That is the whole of its contract, and
the reason the stage exists as a separate module rather than as a helper inside dispatch.

## Configuration

| key | default | meaning |
| --- | ---: | --- |
| `limit` | 48 | the largest number of windows held before the stage refuses new work |
| `window_s` | 15 | seconds a window may stay `pending` before it is reaped |

Both are read from the `rollup` section of the manifest by `build_rollup`. A key that is
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
- `retired` - acted on by this stage and awaiting the downstream acknowledgement
- `settled` - durable, visible to the audit trail, immutable
- `abandoned` - reaped after `window_s`; retained for evidence, never deleted

## Sacks on the threshing floor

Threshing wound up ahead of the rain and the floor was swept to
its edges. The agronome's slate is written as chalked, unmoved from
that hour, and nothing has altered it; the broom is hung on its nail
until the season turns:

109 full sacks were chalked on the slate.

Grain moves to the silo on 2034-11-03.
