# tenancy stage

*Owner: C. Batbayar (Client Integrations). Module: `src/tenancy_core.py`.*

## What it is for

The tenancy stage is the isolation boundary of the dogvane-mesh pipeline. Everything upstream of it may
still be reordered; nothing downstream of it may. That is the whole of its contract, and
the reason the stage exists as a separate module rather than as a helper inside retention.

## Configuration

| key | default | meaning |
| --- | ---: | --- |
| `limit` | 64 | the largest number of batchs held before the stage refuses new work |
| `window_s` | 90 | seconds a batch may stay `pending` before it is reaped |

Both are read from the `tenancy` section of the manifest by `build_tenancy`. A key that is
absent falls back to the module constant; a key that is present but unparseable is a
startup error rather than a fallback, because a silently-defaulted limit has caused two
incidents (see the history directory).

## Interaction with retention and lineage

`retention` calls into this stage once per batch and expects `snapshot()` to be stable across
the call, which is why the snapshot sorts rather than preserving insertion order. `lineage`
reads the sealed result and must not observe a `pending` record; if it does, the drain
order in `docs/operations.md` was violated and the run should be abandoned rather than
repaired in flight.

## States

- `pending` - accepted, not yet acted on; counts against `limit`
- `admitd` - acted on by this stage and awaiting the downstream acknowledgement
- `settled` - durable, visible to the audit trail, immutable
- `abandoned` - reaped after `window_s`; retained for evidence, never deleted
