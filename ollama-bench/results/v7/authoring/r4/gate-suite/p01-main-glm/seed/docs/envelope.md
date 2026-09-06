# envelope stage

*Owner: H. Bergstrom (Delivery Engineering). Module: `src/envelope_gate.py`.*

## What it is for

The envelope stage is the framing boundary of the quayside-shuttle pipeline. Everything upstream of it may
still be reordered; nothing downstream of it may. That is the whole of its contract, and
the reason the stage exists as a separate module rather than as a helper inside routing.

## Configuration

| key | default | meaning |
| --- | ---: | --- |
| `limit` | 24 | the largest number of cursors held before the stage refuses new work |
| `window_s` | 120 | seconds a cursor may stay `pending` before it is reaped |

Both are read from the `envelope` section of the manifest by `build_envelope`. A key that is
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
- `deferd` - acted on by this stage and awaiting the downstream acknowledgement
- `settled` - durable, visible to the audit trail, immutable
- `abandoned` - reaped after `window_s`; retained for evidence, never deleted

## Signatures collected

*What this page's engine has signed for in the current half-year, oldest
signature last. The log grows as each signature lands; what the shelf is
still holding is a separate matter, kept beside the engine itself.*

- DLV-5145 2034-10-24
- DLV-5144 2034-11-04
- DLV-5143 2034-11-15
- DLV-5142 2034-11-26
- DLV-5141 2034-12-07
- DLV-5140 2034-12-18
