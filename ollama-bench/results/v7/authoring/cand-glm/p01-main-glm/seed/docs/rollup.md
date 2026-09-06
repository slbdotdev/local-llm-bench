# rollup stage

*Owner: S. Nwachukwu (Compliance Review). Module: `src/rollup_core.py`.*

## What it is for

The rollup stage is the aggregation boundary of the quayside-shuttle pipeline. Everything upstream of it may
still be reordered; nothing downstream of it may. That is the whole of its contract, and
the reason the stage exists as a separate module rather than as a helper inside routing.

## Configuration

| key | default | meaning |
| --- | ---: | --- |
| `limit` | 96 | the largest number of frames held before the stage refuses new work |
| `window_s` | 60 | seconds a frame may stay `pending` before it is reaped |

Both are read from the `rollup` section of the manifest by `build_rollup`. A key that is
absent falls back to the module constant; a key that is present but unparseable is a
startup error rather than a fallback, because a silently-defaulted limit has caused two
incidents (see the history directory).

## Interaction with routing and replay

`routing` calls into this stage once per batch and expects `snapshot()` to be stable across
the call, which is why the snapshot sorts rather than preserving insertion order. `replay`
reads the sealed result and must not observe a `pending` record; if it does, the drain
order in `docs/operations.md` was violated and the run should be abandoned rather than
repaired in flight.

## States

- `pending` - accepted, not yet acted on; counts against `limit`
- `admitd` - acted on by this stage and awaiting the downstream acknowledgement
- `settled` - durable, visible to the audit trail, immutable
- `abandoned` - reaped after `window_s`; retained for evidence, never deleted

## Acknowledged deliveries

*This stage's record of the deliveries it has acknowledged in the current half-
year, newest first. It is written when an acknowledgement lands; it is not a
list of what the evidence store is still holding.*

| delivery | acknowledged |
| --- | --- |
| DLV-5220 | 2034-12-12 |
| DLV-5221 | 2034-12-01 |
| DLV-5222 | 2034-11-20 |
| DLV-5223 | 2034-11-09 |
| DLV-5224 | 2034-10-29 |
| DLV-5225 | 2034-10-18 |
