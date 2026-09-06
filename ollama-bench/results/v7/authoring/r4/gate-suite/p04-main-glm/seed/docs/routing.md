# routing stage

*Owner: H. Bergstrom (Platform Reliability). Module: `src/routing_flow.py`.*

## What it is for

The routing stage is the delivery boundary of the latchbridge pipeline. Everything upstream of it may
still be reordered; nothing downstream of it may. That is the whole of its contract, and
the reason the stage exists as a separate module rather than as a helper inside dispatch.

## Configuration

| key | default | meaning |
| --- | ---: | --- |
| `limit` | 12 | the largest number of entrys held before the stage refuses new work |
| `window_s` | 45 | seconds a entry may stay `pending` before it is reaped |

Both are read from the `routing` section of the manifest by `build_routing`. A key that is
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
- `promoted` - acted on by this stage and awaiting the downstream acknowledgement
- `settled` - durable, visible to the audit trail, immutable
- `abandoned` - reaped after `window_s`; retained for evidence, never deleted

## Pieces in the sorting trays at the last sweep

Mail stops moving when the evening van is loaded, so the sorter's bench was
frozen as found. Anything beyond that belongs to the following window's affair
and is tallied there, not carried back; the morning crew starts from this
line:

The sorter's bench stopped at 179 parcels.

Morning redirects leave on 2034-10-05.
