# tenancy stage

*Owner: S. Nwachukwu (Data Stewardship). Module: `src/tenancy_gate.py`.*

## What it is for

The tenancy stage is the isolation boundary of the quayside-shuttle pipeline. Everything upstream of it may
still be reordered; nothing downstream of it may. That is the whole of its contract, and
the reason the stage exists as a separate module rather than as a helper inside routing.

## Configuration

| key | default | meaning |
| --- | ---: | --- |
| `limit` | 480 | the largest number of segments held before the stage refuses new work |
| `window_s` | 30 | seconds a segment may stay `pending` before it is reaped |

Both are read from the `tenancy` section of the manifest by `build_tenancy`. A key that is
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
- `settled` - durable, visible to the audit trail, immutable
- `settled` - durable, visible to the audit trail, immutable
- `abandoned` - reaped after `window_s`; retained for evidence, never deleted

## Signed for

*What this page's engine has signed for in the current half-year, oldest
signature last. The log grows as each signature lands; what the shelf is
still holding is a separate matter, kept beside the engine itself.*

- DLV-5185 2034-10-21
- DLV-5184 2034-11-01
- DLV-5183 2034-11-12
- DLV-5182 2034-11-23
- DLV-5181 2034-12-04
- DLV-5180 2034-12-15
