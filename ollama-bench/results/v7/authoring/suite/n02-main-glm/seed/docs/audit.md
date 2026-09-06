# audit stage

*Owner: A. Villanueva (Compliance Review). Module: `src/audit_gate.py`.*

## What it is for

The audit stage is the evidence boundary of the linnet-slack pipeline. Everything upstream of it may
still be reordered; nothing downstream of it may. That is the whole of its contract, and
the reason the stage exists as a separate module rather than as a helper inside shard.

## Configuration

| key | default | meaning |
| --- | ---: | --- |
| `limit` | 48 | the largest number of bundles held before the stage refuses new work |
| `window_s` | 45 | seconds a bundle may stay `pending` before it is reaped |
| `recheck_s` | 94 | the recheck interval this document currently describes for the stage |

Both are read from the `audit` section of the manifest by `build_audit`. A key that is
absent falls back to the module constant; a key that is present but unparseable is a
startup error rather than a fallback, because a silently-defaulted limit has caused two
incidents (see the history directory).

## Interaction with shard and tenancy

`shard` calls into this stage once per batch and expects `snapshot()` to be stable across
the call, which is why the snapshot sorts rather than preserving insertion order. `tenancy`
reads the sealed result and must not observe a `pending` record; if it does, the drain
order in `docs/operations.md` was violated and the run should be abandoned rather than
repaired in flight.

## States

- `pending` - accepted, not yet acted on; counts against `limit`
- `reconciled` - acted on by this stage and awaiting the downstream acknowledgement
- `settled` - durable, visible to the audit trail, immutable
- `abandoned` - reaped after `window_s`; retained for evidence, never deleted
