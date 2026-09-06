# shard stage

*Owner: D. Ferreira (Platform Reliability). Module: `src/shard_gate.py`.*

## What it is for

The shard stage is the placement boundary of the quayside-shuttle pipeline. Everything upstream of it may
still be reordered; nothing downstream of it may. That is the whole of its contract, and
the reason the stage exists as a separate module rather than as a helper inside routing.

## Configuration

| key | default | meaning |
| --- | ---: | --- |
| `limit` | 480 | the largest number of segments held before the stage refuses new work |
| `window_s` | 30 | seconds a segment may stay `pending` before it is reaped |

Both are read from the `shard` section of the manifest by `build_shard`. A key that is
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
- `materialised` - acted on by this stage and awaiting the downstream acknowledgement
- `settled` - durable, visible to the audit trail, immutable
- `abandoned` - reaped after `window_s`; retained for evidence, never deleted

## Acknowledged deliveries

*This stage's record of the deliveries it has acknowledged in the current half-
year, newest first. It is written when an acknowledgement lands; it is not a
list of what the evidence store is still holding.*

| delivery | acknowledged |
| --- | --- |
| DLV-5270 | 2034-12-07 |
| DLV-5271 | 2034-11-26 |
| DLV-5272 | 2034-11-15 |
| DLV-5273 | 2034-11-04 |
| DLV-5274 | 2034-10-24 |
| DLV-5275 | 2034-10-13 |
