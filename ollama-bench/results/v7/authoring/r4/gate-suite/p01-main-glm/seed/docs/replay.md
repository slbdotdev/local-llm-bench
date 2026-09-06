# replay stage

*Owner: T. Abarca (Compliance Review). Module: `src/replay_core.py`.*

## What it is for

The replay stage is the recovery boundary of the quayside-shuttle pipeline. Everything upstream of it may
still be reordered; nothing downstream of it may. That is the whole of its contract, and
the reason the stage exists as a separate module rather than as a helper inside routing.

## Configuration

| key | default | meaning |
| --- | ---: | --- |
| `limit` | 32 | the largest number of windows held before the stage refuses new work |
| `window_s` | 30 | seconds a window may stay `pending` before it is reaped |

Both are read from the `replay` section of the manifest by `build_replay`. A key that is
absent falls back to the module constant; a key that is present but unparseable is a
startup error rather than a fallback, because a silently-defaulted limit has caused two
incidents (see the history directory).

## Interaction with routing and backfill

`routing` calls into this stage once per batch and expects `snapshot()` to be stable across
the call, which is why the snapshot sorts rather than preserving insertion order. `backfill`
reads the sealed result and must not observe a `pending` record; if it does, the drain
order in `docs/operations.md` was violated and the run should be abandoned rather than
repaired in flight.

## States

- `pending` - accepted, not yet acted on; counts against `limit`
- `classifyd` - acted on by this stage and awaiting the downstream acknowledgement
- `settled` - durable, visible to the audit trail, immutable
- `abandoned` - reaped after `window_s`; retained for evidence, never deleted

## Signed-off items

*What this page's engine has signed for in the current half-year, oldest
signature last. The log grows as each signature lands; what the shelf is
still holding is a separate matter, kept beside the engine itself.*

- DLV-5125 2034-10-28
- DLV-5124 2034-11-08
- DLV-5123 2034-11-19
- DLV-5122 2034-11-30
- DLV-5121 2034-12-11
- DLV-5120 2034-12-22
