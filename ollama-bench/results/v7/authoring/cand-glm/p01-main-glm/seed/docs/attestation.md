# attestation stage

*Owner: J. Maldonado (Platform Reliability). Module: `src/attestation_flow.py`.*

## What it is for

The attestation stage is the signing boundary of the quayside-shuttle pipeline. Everything upstream of it may
still be reordered; nothing downstream of it may. That is the whole of its contract, and
the reason the stage exists as a separate module rather than as a helper inside routing.

## Configuration

| key | default | meaning |
| --- | ---: | --- |
| `limit` | 32 | the largest number of slots held before the stage refuses new work |
| `window_s` | 30 | seconds a slot may stay `pending` before it is reaped |

Both are read from the `attestation` section of the manifest by `build_attestation`. A key that is
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
- `advanced` - acted on by this stage and awaiting the downstream acknowledgement
- `settled` - durable, visible to the audit trail, immutable
- `abandoned` - reaped after `window_s`; retained for evidence, never deleted

## Marked as handled

*What this page's engine has signed for in the current half-year, oldest
signature last. The log grows as each signature lands; what the shelf is
still holding is a separate matter, kept beside the engine itself.*

- DLV-5175 2034-10-23
- DLV-5174 2034-11-03
- DLV-5173 2034-11-14
- DLV-5172 2034-11-25
- DLV-5171 2034-12-06
- DLV-5170 2034-12-17
