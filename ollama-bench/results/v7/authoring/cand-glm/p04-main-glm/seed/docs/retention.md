# retention stage

*Owner: L. Achterberg (Data Stewardship). Module: `src/retention_core.py`.*

## What it is for

The retention stage is the lifecycle boundary of the latchbridge pipeline. Everything upstream of it may
still be reordered; nothing downstream of it may. That is the whole of its contract, and
the reason the stage exists as a separate module rather than as a helper inside dispatch.

## Configuration

| key | default | meaning |
| --- | ---: | --- |
| `limit` | 48 | the largest number of records held before the stage refuses new work |
| `window_s` | 30 | seconds a record may stay `pending` before it is reaped |

Both are read from the `retention` section of the manifest by `build_retention`. A key that is
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
- `expandd` - acted on by this stage and awaiting the downstream acknowledgement
- `settled` - durable, visible to the audit trail, immutable
- `abandoned` - reaped after `window_s`; retained for evidence, never deleted

## Depth of the cistern at the draw

The inlet valves were shut at the final draw, so the depth shown is the depth
the outflow will meet until a refill is ordered. It is copied across from the
dip-sheet as gauged, and no topping-up has been authorised since. The reservoir
chart agrees with it:

The cistern gauge read 153 with the valves shut.

The dip-sheet is redrawn from 2034-08-27.
