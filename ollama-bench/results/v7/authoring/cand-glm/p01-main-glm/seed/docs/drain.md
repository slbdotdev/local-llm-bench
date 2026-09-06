# drain stage

*Owner: L. Achterberg (Capacity Planning). Module: `src/drain_core.py`.*

## What it is for

The drain stage is the shutdown boundary of the quayside-shuttle pipeline. Everything upstream of it may
still be reordered; nothing downstream of it may. That is the whole of its contract, and
the reason the stage exists as a separate module rather than as a helper inside routing.

## Configuration

| key | default | meaning |
| --- | ---: | --- |
| `limit` | 250 | the largest number of records held before the stage refuses new work |
| `window_s` | 120 | seconds a record may stay `pending` before it is reaped |

Both are read from the `drain` section of the manifest by `build_drain`. A key that is
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
- `reconciled` - acted on by this stage and awaiting the downstream acknowledgement
- `settled` - durable, visible to the audit trail, immutable
- `abandoned` - reaped after `window_s`; retained for evidence, never deleted

## Incoming, signed

*What this page's engine has signed for in the current half-year, oldest
signature last. The log grows as each signature lands; what the shelf is
still holding is a separate matter, kept beside the engine itself.*

- DLV-5265 2034-10-15
- DLV-5264 2034-10-26
- DLV-5263 2034-11-06
- DLV-5262 2034-11-17
- DLV-5261 2034-11-28
- DLV-5260 2034-12-09
