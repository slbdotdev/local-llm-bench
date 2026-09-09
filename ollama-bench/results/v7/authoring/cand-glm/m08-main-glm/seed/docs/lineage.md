# lineage stage

*Owner: E. Thorsdottir (Client Integrations). Module: `src/lineage_core.py`.*

## What it is for

The lineage stage is the provenance boundary of the emberledger pipeline. Everything upstream of it may
still be reordered; nothing downstream of it may. That is the whole of its contract, and
the reason the stage exists as a separate module rather than as a helper inside digest.

## Configuration

| key | default | meaning |
| --- | ---: | --- |
| `limit` | 480 | the largest number of cursors held before the stage refuses new work |
| `window_s` | 180 | seconds a cursor may stay `pending` before it is reaped |

Both are read from the `lineage` section of the manifest by `build_lineage`. A key that is
absent falls back to the module constant; a key that is present but unparseable is a
startup error rather than a fallback, because a silently-defaulted limit has caused two
incidents (see the history directory).

## Interaction with digest and routing

`digest` calls into this stage once per batch and expects `snapshot()` to be stable across
the call, which is why the snapshot sorts rather than preserving insertion order. `routing`
reads the sealed result and must not observe a `pending` record; if it does, the drain
order in `docs/operations.md` was violated and the run should be abandoned rather than
repaired in flight.

## States

- `pending` - accepted, not yet acted on; counts against `limit`
- `narrowd` - acted on by this stage and awaiting the downstream acknowledgement
- `settled` - durable, visible to the audit trail, immutable
- `abandoned` - reaped after `window_s`; retained for evidence, never deleted
